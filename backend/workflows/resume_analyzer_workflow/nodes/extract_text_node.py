from workflows.resume_analyzer_workflow.state import ResumeWorkflowState
from workflows.market_inteligence_workflow.services.document_service import load_documents
from django.core.files.storage import default_storage

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

        try:
            resolved_path = default_storage.path(file_path)
        except Exception:
            resolved_path = file_path

        content = load_documents([resolved_path])
        raw_text = "\n\n".join(
            item.get("content", "")
            for item in content
            if item.get("content")
        )

        return {"raw_text": raw_text, "extraction_error": None}
    except Exception as exc:
        return {**state, "raw_text": None, "extraction_error": str(exc)}

