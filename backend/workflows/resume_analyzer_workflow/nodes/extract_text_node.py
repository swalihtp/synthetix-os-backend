import logging
from django.core.files.storage import default_storage

from workflows.market_inteligence_workflow.services.document_service import (
    load_documents,
)
from workflows.resume_analyzer_workflow.state import ResumeWorkflowState

logger = logging.getLogger(__name__)

def extract_text_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Pipeline task: file.extract_text
    Parses PDF / DOCX / TXT and returns clean plain text.
    Replace the stub below with your actual file-extraction logic.
    """
    try:
        file_path = state.get("file_path")

        if not file_path:
            raise ValueError("file_path is required")

        exists = default_storage.exists(file_path)
        logger.info(
            "[resume.extract_text] file_path=%s exists=%s",
            file_path,
            exists,
        )

        if not exists:
            raise FileNotFoundError(
                f"Resume file '{file_path}' does not exist in default_storage"
            )

        content = load_documents([file_path])
        raw_text = "\n\n".join(
            item.get("content", "")
            for item in content
            if item.get("content")
        ).strip()

        logger.info("[resume.extract_text] extraction succeeded for file_path=%s", file_path)

        return {"raw_text": raw_text, "extraction_error": None}
    except Exception as exc:
        logger.exception("[resume.extract_text] extraction failed for file_path=%s", state.get("file_path"))
        return {**state, "raw_text": None, "extraction_error": str(exc)}

