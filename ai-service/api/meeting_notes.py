from __future__ import annotations

import json
import logging
import re

import httpx
from fastapi import APIRouter, HTTPException
from openai import APITimeoutError, RateLimitError
from pydantic import BaseModel, Field, ValidationError

from services.llm_service import llm

router = APIRouter()
logger = logging.getLogger(__name__)


class MeetingNotesRequest(BaseModel):
    raw_transcript: str
    file_type: str | None = None
    summary_style: str | None = None


class MeetingTopic(BaseModel):
    topic: str = ""
    speakers: list[str] = Field(default_factory=list)
    summary: str = ""


class MeetingDecision(BaseModel):
    decision: str = ""
    made_by: str | None = None
    context: str = ""


class MeetingActionItem(BaseModel):
    task: str = ""
    owner: str | None = None
    due: str | None = None
    topic: str = ""


class MeetingSummary(BaseModel):
    title: str = ""
    summary_style: str | None = None
    blockers: list[str] = Field(default_factory=list)
    next_steps: str = ""
    summary: str = ""


class MeetingNotesResponse(BaseModel):
    topics: list[MeetingTopic] = Field(default_factory=list)
    decisions: list[MeetingDecision] = Field(default_factory=list)
    action_items: list[MeetingActionItem] = Field(default_factory=list)
    meeting_summary: MeetingSummary = Field(default_factory=MeetingSummary)


structured_llm = llm.with_structured_output(MeetingNotesResponse)


SYSTEM_PROMPT_FOR_MEETING_NOTES = """
You are an AI meeting notes assistant.

Your responsibilities:
1. Detect the major topics discussed in the meeting.
2. Extract explicit decisions with the person responsible.
3. Extract concrete action items with owners and due dates when explicitly stated.
4. Produce a concise structured meeting summary.
5. Return structured data only.

Rules:
- Use only the provided transcript chunk
- Do not invent speakers, decisions, tasks, owners, or due dates
- Keep summaries concise and factual
- If a fact is missing, leave the field empty or null
- If no blockers, decisions, or action items are present in the chunk, return empty lists
"""


MEETING_NOTES_JSON_INSTRUCTIONS = """
Return ONLY valid JSON matching this schema:
{
  "topics": [{"topic": "", "speakers": [], "summary": ""}],
  "decisions": [{"decision": "", "made_by": null, "context": ""}],
  "action_items": [{"task": "", "owner": null, "due": null, "topic": ""}],
  "meeting_summary": {
    "title": "",
    "summary_style": null,
    "blockers": [],
    "next_steps": "",
    "summary": ""
  }
}

Do not wrap the JSON in markdown fences.
Do not include any extra text before or after the JSON.
"""


def split_text(text: str, chunk_size: int = 6000, overlap: int = 500) -> list[str]:
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        return [""]

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    overlap = max(0, min(overlap, chunk_size - 1))
    chunks: list[str] = []
    start = 0
    total_length = len(cleaned_text)

    while start < total_length:
        end = min(total_length, start + chunk_size)
        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= total_length:
            break

        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1
        start = next_start

    return chunks or [cleaned_text]


def _normalize_key(value: str | None) -> str:
    normalized = " ".join((value or "").split()).casefold()
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def _split_into_sentences(text: str) -> list[str]:
    normalized_text = " ".join((text or "").split())
    if not normalized_text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+|\n+", normalized_text)
    return [sentence.strip(" -•\t") for sentence in sentences if sentence.strip(" -•\t")]


def _merge_text_values(values: list[str]) -> str:
    seen: set[str] = set()
    merged: list[str] = []

    for value in values:
        for sentence in _split_into_sentences(value):
            key = _normalize_key(sentence)
            if not key or key in seen:
                continue
            seen.add(key)
            merged.append(sentence)

    return " ".join(merged).strip()


def extract_json_from_text(text: str) -> dict:
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise ValueError("Empty model output.")

    fenced_block_match = re.search(
        r"```(?:json)?\s*(.*?)\s*```",
        cleaned_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fenced_block_match:
        fenced_text = fenced_block_match.group(1).strip()
        try:
            parsed = json.loads(fenced_text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    try:
        parsed = json.loads(cleaned_text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start_index = cleaned_text.find("{")
    while start_index != -1:
        depth = 0
        in_string = False
        escape = False
        for index in range(start_index, len(cleaned_text)):
            character = cleaned_text[index]
            if in_string:
                if escape:
                    escape = False
                elif character == "\\":
                    escape = True
                elif character == '"':
                    in_string = False
                continue

            if character == '"':
                in_string = True
                continue

            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    candidate = cleaned_text[start_index : index + 1].strip()
                    try:
                        parsed = json.loads(candidate)
                        if isinstance(parsed, dict):
                            return parsed
                    except json.JSONDecodeError:
                        break
                    break

        start_index = cleaned_text.find("{", start_index + 1)

    raise ValueError("No valid JSON object found in model output.")


def _get_llm_text(output) -> str:
    if isinstance(output, str):
        return output

    content = getattr(output, "content", None)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text", item)))
            else:
                parts.append(str(item))
        if parts:
            return "\n".join(parts)

    if output is None:
        return ""

    return str(output)


def _coerce_meeting_notes_response(data) -> MeetingNotesResponse:
    if isinstance(data, MeetingNotesResponse):
        return data
    if isinstance(data, dict):
        return MeetingNotesResponse.model_validate(data)
    if hasattr(data, "model_dump"):
        return MeetingNotesResponse.model_validate(data.model_dump())
    return MeetingNotesResponse.model_validate(data)


def _build_meeting_notes_prompt(
    chunk: str,
    index: int,
    total_chunks: int,
    file_type: str | None = None,
    summary_style: str | None = None,
    json_only: bool = False,
) -> str:
    prompt = f"""
{SYSTEM_PROMPT_FOR_MEETING_NOTES}

FILE TYPE:
{file_type or ""}

SUMMARY STYLE:
{summary_style or ""}

CHUNK INFO:
This is chunk {index} of {total_chunks}.

TRANSCRIPT CHUNK:
{chunk}
"""

    if json_only:
        prompt = f"{prompt}\n{MEETING_NOTES_JSON_INSTRUCTIONS}"

    return prompt


def _build_repair_prompt(invalid_output: str, validation_error: str) -> str:
    return f"""
{SYSTEM_PROMPT_FOR_MEETING_NOTES}

The previous output was invalid.

INVALID OUTPUT:
{invalid_output}

VALIDATION ERROR:
{validation_error}

{MEETING_NOTES_JSON_INSTRUCTIONS}

Return a corrected JSON object now.
"""


def _parse_meeting_notes_response(raw_output: str) -> MeetingNotesResponse:
    parsed_data = extract_json_from_text(raw_output)
    return MeetingNotesResponse.model_validate(parsed_data)


def _generate_meeting_notes_response(
    prompt: str,
) -> MeetingNotesResponse:
    raw_text = ""

    try:
        structured_output = structured_llm.invoke(prompt)
        response = _coerce_meeting_notes_response(structured_output)
        logger.info("Meeting notes structured output succeeded.")
        return response
    except Exception:
        logger.warning("Meeting notes structured output failed; falling back to raw JSON mode.", exc_info=True)

    try:
        raw_output = llm.invoke(prompt)
        raw_text = _get_llm_text(raw_output)
        logger.info("Meeting notes raw model output length: %s", len(raw_text))
        response = _parse_meeting_notes_response(raw_text)
        return response
    except (ValueError, json.JSONDecodeError, ValidationError) as exc:
        logger.warning("Meeting notes raw output parsing failed: %s", exc, exc_info=True)

        repair_prompt = _build_repair_prompt(
            invalid_output=raw_text,
            validation_error=str(exc),
        )

        try:
            repair_output = llm.invoke(repair_prompt)
            repair_text = _get_llm_text(repair_output)
            logger.info("Meeting notes repair output length: %s", len(repair_text))
            response = _parse_meeting_notes_response(repair_text)
            logger.info("Meeting notes repair succeeded.")
            return response
        except (ValueError, json.JSONDecodeError, ValidationError) as repair_exc:
            logger.exception("Meeting notes repair failed after retry.")
            raise HTTPException(
                status_code=500,
                detail="Meeting notes generation failed after retry. Please try again or switch models.",
            ) from repair_exc


def summarize_chunk(
    chunk: str,
    index: int,
    total_chunks: int,
    file_type: str | None = None,
    summary_style: str | None = None,
) -> MeetingNotesResponse:
    chunk_prompt = _build_meeting_notes_prompt(
        chunk=chunk,
        index=index,
        total_chunks=total_chunks,
        file_type=file_type,
        summary_style=summary_style,
        json_only=True,
    )
    return _generate_meeting_notes_response(prompt=chunk_prompt)


def merge_summaries(partial_summaries: list[MeetingNotesResponse]) -> MeetingNotesResponse:
    if not partial_summaries:
        return MeetingNotesResponse()

    topic_map: dict[str, MeetingTopic] = {}
    topic_order: list[str] = []

    decision_map: dict[str, MeetingDecision] = {}
    decision_order: list[str] = []

    action_item_map: dict[str, MeetingActionItem] = {}
    action_item_order: list[str] = []

    blockers: list[str] = []
    blocker_keys: set[str] = set()
    titles: list[str] = []
    summary_styles: list[str] = []
    summaries: list[str] = []
    next_steps_values: list[str] = []

    for partial in partial_summaries:
        if partial.meeting_summary.title:
            titles.append(partial.meeting_summary.title)

        if partial.meeting_summary.summary_style:
            summary_styles.append(partial.meeting_summary.summary_style)

        if partial.meeting_summary.summary:
            summaries.append(partial.meeting_summary.summary)

        if partial.meeting_summary.next_steps:
            next_steps_values.append(partial.meeting_summary.next_steps)

        for blocker in partial.meeting_summary.blockers:
            blocker_key = _normalize_key(blocker)
            if blocker_key and blocker_key not in blocker_keys:
                blocker_keys.add(blocker_key)
                blockers.append(blocker)

        for topic in partial.topics:
            topic_key = _normalize_key(topic.topic)
            if not topic_key:
                continue

            current_topic = topic_map.get(topic_key)
            if current_topic is None:
                topic_map[topic_key] = MeetingTopic(
                    topic=topic.topic,
                    speakers=list(dict.fromkeys(topic.speakers)),
                    summary=topic.summary,
                )
                topic_order.append(topic_key)
                continue

            merged_speakers = list(dict.fromkeys(current_topic.speakers + topic.speakers))
            current_topic.speakers = merged_speakers
            if topic.summary:
                current_topic.summary = _merge_text_values([current_topic.summary, topic.summary])

        for decision in partial.decisions:
            decision_key = "|".join(
                [
                    _normalize_key(decision.decision),
                    _normalize_key(decision.made_by),
                ]
            )
            if not decision_key.strip("|"):
                continue

            current_decision = decision_map.get(decision_key)
            if current_decision is None:
                decision_map[decision_key] = MeetingDecision(
                    decision=decision.decision,
                    made_by=decision.made_by,
                    context=decision.context,
                )
                decision_order.append(decision_key)
                continue

            if not current_decision.made_by and decision.made_by:
                current_decision.made_by = decision.made_by
            if decision.context:
                current_decision.context = _merge_text_values(
                    [current_decision.context, decision.context]
                )

        for action_item in partial.action_items:
            action_item_key = "|".join(
                [
                    _normalize_key(action_item.task),
                    _normalize_key(action_item.owner),
                    _normalize_key(action_item.due),
                    _normalize_key(action_item.topic),
                ]
            )
            if not action_item_key.strip("|"):
                continue

            current_action_item = action_item_map.get(action_item_key)
            if current_action_item is None:
                action_item_map[action_item_key] = MeetingActionItem(
                    task=action_item.task,
                    owner=action_item.owner,
                    due=action_item.due,
                    topic=action_item.topic,
                )
                action_item_order.append(action_item_key)
                continue

            if not current_action_item.owner and action_item.owner:
                current_action_item.owner = action_item.owner
            if not current_action_item.due and action_item.due:
                current_action_item.due = action_item.due
            if not current_action_item.topic and action_item.topic:
                current_action_item.topic = action_item.topic

    merged_title = next((title for title in titles if title.strip()), "")
    merged_summary_style = next((style for style in summary_styles if style.strip()), None)

    merged_topics = [topic_map[key] for key in topic_order]
    merged_decisions = [decision_map[key] for key in decision_order]
    merged_action_items = [action_item_map[key] for key in action_item_order]

    return MeetingNotesResponse(
        topics=merged_topics,
        decisions=merged_decisions,
        action_items=merged_action_items,
        meeting_summary=MeetingSummary(
            title=merged_title,
            summary_style=merged_summary_style,
            blockers=blockers,
            next_steps=_merge_text_values(next_steps_values),
            summary=_merge_text_values(summaries),
        ),
    )


@router.post("/generate-meeting-summary", response_model=MeetingNotesResponse)
async def generate_meeting_summary(state: MeetingNotesRequest):
    try:
        transcript = state.raw_transcript.strip()
        if not transcript:
            raise HTTPException(
                status_code=400,
                detail="raw_transcript cannot be empty.",
            )

        chunks = split_text(transcript)
        partial_summaries = [
            summarize_chunk(
                chunk=chunk,
                index=index,
                total_chunks=len(chunks),
                file_type=state.file_type,
                summary_style=state.summary_style,
            )
            for index, chunk in enumerate(chunks, start=1)
        ]

        response = merge_summaries(partial_summaries)
        return response.model_dump()

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Model is temporarily rate limited. Please retry in a few seconds.",
        )

    except (APITimeoutError, httpx.TimeoutException, TimeoutError):
        raise HTTPException(
            status_code=504,
            detail="Meeting summary generation timed out. Please retry with a smaller transcript or try again shortly.",
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Structured meeting notes generation failed: {exc}",
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Unexpected failure while generating meeting summary.")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate meeting summary. Please try again later.",
        ) from exc
