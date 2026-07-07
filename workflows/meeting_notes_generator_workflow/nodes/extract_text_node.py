import re
from pathlib import Path

from django.core.files.storage import default_storage

from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState
from workflows.market_inteligence_workflow.services.document_service import (
    load_documents,
)


def _resolve_path(file_path: str) -> str:
    try:
        return default_storage.path(file_path)
    except Exception:
        return file_path


def _extract_text_from_vtt_or_srt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8-sig") as file:
        text = file.read()

    text = re.sub(r"^WEBVTT.*?$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(
        r"\d{2}:\d{2}:\d{2}[.,]\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}[.,]\d{3}.*$",
        "",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"\d{2}:\d{2}:\d{2}\s+-->\s+\d{2}:\d{2}:\d{2}.*$",
        "",
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_text_node(state: MeetingWorkflowState) -> MeetingWorkflowState:
    """
    Pipeline task: file.extract_text
    Reads the transcript file and returns clean plain text.
    Handles plain text, PDF, DOCX, and subtitle formats (VTT/SRT).
    """
    try:
        file_path = state.get("file_path")

        if not file_path:
            raise ValueError("file_path is required")

        resolved_path = _resolve_path(file_path)
        suffix = Path(resolved_path).suffix.lower()

        if suffix in {".pdf", ".docx", ".txt"}:
            documents = load_documents([resolved_path])
            raw_transcript = "\n\n".join(
                item.get("content", "")
                for item in documents
                if item.get("content")
            ).strip()
        elif suffix in {".vtt", ".srt"}:
            raw_transcript = _extract_text_from_vtt_or_srt(resolved_path)
        else:
            raise ValueError(f"Unsupported transcript type: {suffix}")

        return {**state, "raw_transcript": raw_transcript, "extraction_error": None}
    except Exception as exc:
        return {**state, "raw_transcript": None, "extraction_error": str(exc)}
