from workflows.email_workflow.state import EmailWorkflowState
from workflows.utils.realtime import send_workflow_update
from workflows.models import EmailExecution, EmailAttachment
from workflows.email_workflow.services.s3_upload import upload_attachment


def extract_attachments_node(state: EmailWorkflowState) -> EmailWorkflowState:

    send_workflow_update(
        state["agent_id"],
        {
            "log": "Extracting Attachments",
            "progress": 40,
            "step": {"index": 4, "name": "Extracting", "status": "runnig"},
        },
    )
    attachments = state["raw_email"].get("attachments", [])

    print("ATTACHMENTS:", attachments)

    email_execution = EmailExecution.objects.get(id=state.get("email_execution_id"))

    for attachment in attachments:

        s3_key = upload_attachment(
            content=attachment["data"],
            filename=attachment["filename"],
            email_execution_id=state["email_execution_id"],
        )

        attachment_record = EmailAttachment.objects.create(
            email_execution=email_execution,
            filename=attachment["filename"],
            mime_type=attachment["mime_type"],
            s3_key=s3_key,
            processing_status="PENDING",
        )

        attachment["db_id"] = str(attachment_record.id)

    send_workflow_update(
        state["agent_id"],
        {
            "log": "Extracted Attachments successfully",
            "progress": 45,
            "step": {"index": 5, "name": "Extracting", "status": "done"},
        },
    )

    return {"attachments": attachments}
