from workflows.email_workflow.state import EmailWorkflowState
from accounts.models import User
from workflows.email_workflow.services.ai.ai_service import store_document_in_croma_db
from integrations.gmail import send_reply
from workflows.utils.realtime import send_workflow_update
from workflows.models import WorkflowExecution, EmailExecution, AIUsageLog
from django.utils import timezone
from agent.models import Agent


def reply_node(state: EmailWorkflowState) -> EmailWorkflowState:

    user = User.objects.get(id=state["user_id"])

    send_workflow_update(
        state["agent_id"],
        {
            "log": "Sending reply",
            "progress": 95,
            "step": {
                "index": 5,
                "name": "Sending reply",
                "status": "running",
            },
        },
    )

    send_reply(
        user,
        state["raw_email"]["from"],
        state["reply_subject"],
        state["reply_body"],
        state["raw_email"]["thread_id"],
    )

    send_workflow_update(
        state["agent_id"],
        {
            "log": "Sending reply",
            "progress": 100,
            "step": {
                "index": 5,
                "name": "Sending reply",
                "status": "done",
            },
        },
    )

    temp = state.get("raw_email", {}).copy()
    temp.pop("attachments", None)

    sres = store_document_in_croma_db(
        temp,
        state["reply_subject"],
        state["reply_body"],
        str(state["user_id"]),
    )

    execution = WorkflowExecution.objects.get(id=state["execution_id"])
    execution.status = "SUCCESS"
    execution.ended_at = timezone.now()
    execution.save(update_fields=["status", "ended_at"])

    agent = Agent.objects.get(id=state["agent_id"])

    email_execution = EmailExecution.objects.get(id=state.get("email_execution_id"))

    email_execution.agent = agent
    email_execution.email_id = state.get("email_id")
    email_execution.thread_id = state.get("raw_email", {}).get("thread_id")
    email_execution.sender = state.get("raw_email").get("from")
    email_execution.recipient = user.email
    email_execution.original_subject = state.get("raw_email", {}).get("subject", "")
    email_execution.original_body = state.get("raw_email").get("body", "")
    email_execution.detected_intent = state.get("intention", {}).get("intention")
    email_execution.confidence_score = state.get("intention", {}).get("confidence")
    email_execution.reply_subject = state.get("reply_subject", "")
    email_execution.reply_body = state.get("reply_body", "")
    email_execution.result = "AUTO_RESOLVED"
    email_execution.review_reason = state.get("reason_for_review", "")
    email_execution.processed_at = timezone.now()

    email_execution.save()

    if sres:
        AIUsageLog.objects.create(
            workflow_execution=execution,
            provider="GEMINI",
            model_name="models/gemini-embedding-2",
            operation="EMBEDDING",
        )

    return state
