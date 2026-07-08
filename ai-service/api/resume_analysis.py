from __future__ import annotations

import json
import logging
import re
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError

from services.llm_service import llm

router = APIRouter()
logger = logging.getLogger(__name__)


class ResumeAnalysisRequest(BaseModel):
    raw_text: str
    job_title: str | None = None
    job_description: str | None = None
    file_type: str | None = None


class ResumeAnalysisResponse(BaseModel):
    sections_found: list[str]
    missing_sections: list[str]
    formatting_issues: list[str]
    clarity_score: float = Field(ge=0, le=1)


class SkillEvaluationResponse(BaseModel):
    extracted_skills: list[str]
    skill_gaps: list[str]
    keyword_hits: int
    keyword_misses: list[str]


class AtsScoringResponse(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    parse_friendly: bool
    issues: list[str]
    recommended_format: str


class FeedbackReportResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    summary: str
    priority_actions: list[str]
    section_feedback: dict[str, str]
    ats_tips: list[str]


class ResumeAnalysisBundleResponse(BaseModel):
    resume_analysis: ResumeAnalysisResponse
    skill_evaluation: SkillEvaluationResponse
    ats_score: AtsScoringResponse
    feedback_report: FeedbackReportResponse


structured_llm = llm.with_structured_output(ResumeAnalysisBundleResponse)

SYSTEM_PROMPT_FOR_RESUME_ANALYSIS = """
You are an expert resume analysis assistant.

Your responsibilities:
1. Analyze resume structure, formatting, section completeness, and clarity.
2. Extract the most relevant skills from the resume.
3. Score ATS compatibility from 0 to 100.
4. Produce a concise feedback report with prioritized actions.
5. Return structured data only.

Rules:
- Use only the provided resume text and optional job context
- Do not hallucinate missing sections, skills, or formatting problems
- clarity_score must be between 0 and 1
- ats_score must be an integer between 0 and 100
- priority_actions must be ordered by impact
"""

RESUME_ANALYSIS_JSON_INSTRUCTIONS = """
Return ONLY valid JSON matching this schema:
{
  "resume_analysis": {
    "sections_found": [],
    "missing_sections": [],
    "formatting_issues": [],
    "clarity_score": 0.0
  },
  "skill_evaluation": {
    "extracted_skills": [],
    "skill_gaps": [],
    "keyword_hits": 0,
    "keyword_misses": []
  },
  "ats_score": {
    "ats_score": 0,
    "parse_friendly": true,
    "issues": [],
    "recommended_format": ""
  },
  "feedback_report": {
    "overall_score": 0,
    "summary": "",
    "priority_actions": [],
    "section_feedback": {},
    "ats_tips": []
  }
}

Do not wrap the JSON in markdown fences.
Do not include any extra text before or after the JSON.
"""


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


def _coerce_resume_response(data) -> ResumeAnalysisBundleResponse:
    if isinstance(data, ResumeAnalysisBundleResponse):
        return data
    if isinstance(data, dict):
        return ResumeAnalysisBundleResponse.model_validate(data)
    if hasattr(data, "model_dump"):
        return ResumeAnalysisBundleResponse.model_validate(data.model_dump())
    return ResumeAnalysisBundleResponse.model_validate(data)


def _build_resume_analysis_prompt(
    state: ResumeAnalysisRequest, json_only: bool = False
) -> str:
    prompt = f"""
{SYSTEM_PROMPT_FOR_RESUME_ANALYSIS}

JOB TITLE:
{state.job_title or ""}

JOB DESCRIPTION:
{state.job_description or ""}

FILE TYPE:
{state.file_type or ""}

RESUME TEXT:
{state.raw_text}
"""

    if json_only:
        prompt = f"{prompt}\n{RESUME_ANALYSIS_JSON_INSTRUCTIONS}"

    return prompt


def _build_repair_prompt(invalid_output: str, validation_error: str) -> str:
    return f"""
{SYSTEM_PROMPT_FOR_RESUME_ANALYSIS}

The previous output was invalid.

INVALID OUTPUT:
{invalid_output}

VALIDATION ERROR:
{validation_error}

{RESUME_ANALYSIS_JSON_INSTRUCTIONS}

Return a corrected JSON object now.
"""


def _parse_resume_response(raw_output: str) -> ResumeAnalysisBundleResponse:
    parsed_data = extract_json_from_text(raw_output)
    return ResumeAnalysisBundleResponse.model_validate(parsed_data)


def _generate_resume_analysis_response(prompt: str) -> ResumeAnalysisBundleResponse:
    raw_text = ""

    try:
        structured_output = structured_llm.invoke(prompt)
        response = _coerce_resume_response(structured_output)
        logger.info("Resume analysis structured output succeeded.")
        return response
    except Exception:
        logger.warning(
            "Resume analysis structured output failed; falling back to raw JSON mode.",
            exc_info=True,
        )

    try:
        raw_output = llm.invoke(prompt)
        raw_text = _get_llm_text(raw_output)
        logger.info("Resume analysis raw model output length: %s", len(raw_text))
        response = _parse_resume_response(raw_text)
        return response
    except (ValueError, json.JSONDecodeError, ValidationError) as exc:
        logger.warning(
            "Resume analysis raw output parsing failed: %s", exc, exc_info=True
        )

        repair_prompt = _build_repair_prompt(
            invalid_output=raw_text,
            validation_error=str(exc),
        )

        try:
            repair_output = llm.invoke(repair_prompt)
            repair_text = _get_llm_text(repair_output)
            logger.info("Resume analysis repair output length: %s", len(repair_text))
            response = _parse_resume_response(repair_text)
            logger.info("Resume analysis repair succeeded.")
            return response
        except (ValueError, json.JSONDecodeError, ValidationError) as repair_exc:
            logger.exception("Resume analysis repair failed after retry.")
            raise HTTPException(
                status_code=500,
                detail="Resume analysis generation failed after retry. Please try again or switch models.",
            ) from repair_exc


@router.post("/analyze-resume")
async def analyze_resume(state: ResumeAnalysisRequest):
    print('hi')
    print(len(state.raw_text))

    try:
        start = time.time()
        print("Request received")
        final_prompt = _build_resume_analysis_prompt(state, json_only=True)
        print(final_prompt[:500])
        print(f"Prompt built in {time.time() - start:.2f}s")
        response = _generate_resume_analysis_response(final_prompt)
        print(f"Total {time.time() - start:.2f}s")
        return response.model_dump()

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Unexpected failure while analyzing resume.")
        raise HTTPException(status_code=500, detail=str(exc))
