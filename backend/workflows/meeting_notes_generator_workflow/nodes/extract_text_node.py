import logging
import re
from pathlib import Path

from django.core.files.storage import default_storage

from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState
from workflows.market_inteligence_workflow.services.document_service import (
    load_documents,
)

logger = logging.getLogger(__name__)

def _extract_text_from_vtt_or_srt_text(text: str) -> str:

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

        exists = default_storage.exists(file_path)
        logger.info(
            "[meeting_notes.extract_text] file_path=%s exists=%s",
            file_path,
            exists,
        )

        if not exists:
            raise FileNotFoundError(
                f"Meeting notes file '{file_path}' does not exist in default_storage"
            )

        suffix = Path(file_path).suffix.lower()

        if suffix in {".pdf", ".docx", ".txt"}:
            documents = load_documents([file_path])
            raw_transcript = "\n\n".join(
                item.get("content", "")
                for item in documents
                if item.get("content")
            ).strip()
        elif suffix in {".vtt", ".srt"}:
            with default_storage.open(file_path, "rb") as transcript_file:
                raw_transcript = _extract_text_from_vtt_or_srt_text(
                    transcript_file.read().decode("utf-8-sig", errors="replace")
                )
        else:
            raise ValueError(f"Unsupported transcript type: {suffix}")

        logger.info(
            "[meeting_notes.extract_text] extraction succeeded for file_path=%s",
            file_path,
        )

        return {**state, "raw_transcript": raw_transcript, "extraction_error": None}
    except Exception as exc:
        logger.exception(
            "[meeting_notes.extract_text] extraction failed for file_path=%s",
            state.get("file_path"),
        )
        return {**state, "raw_transcript": None, "extraction_error": str(exc)}
