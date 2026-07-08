from workflows.email_workflow.state import EmailWorkflowState
from workflows.email_workflow.services.documents.processer import process_document
from workflows.utils.realtime import send_workflow_update


def document_processing_node(state: EmailWorkflowState) -> EmailWorkflowState:

    extracted_documents = []
    unsupported_files = []

    send_workflow_update(
        state["agent_id"],
        {
            "log": "Document Processing",
            "progress": 50,
            "step": {"index": 6, "name": "Processing", "status": "running"},
        },
    )

    for attachment in state["attachments"]:

        try:
            text = process_document(attachment)

            if text:
                extracted_documents.append(text)

        except ValueError as e:

            unsupported_files.append(
                {
                    "filename": attachment.get("filename"),
                    "mime_type": attachment.get("mime_type"),
                    "reason": str(e),
                }
            )

    state["extracted_documents"] = extracted_documents

    # Human review trigger
    if unsupported_files:

        state["requires_human"] = True

        state["reason_for_review"] = "Unsupported document types detected"

        state["unsupported_files"] = unsupported_files

    send_workflow_update(
        state["agent_id"],
        {
            "log": "Document Processed Successfully",
            "progress": 55,
            "step": {"index": 7, "name": "Processing", "status": "done"},
        },
    )

    return state
