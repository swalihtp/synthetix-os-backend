from accounts.models import User
from workflows.email_workflow.state import EmailWorkflowState
from workflows.models import (
    WorkflowExecution,
    EmailExecutionResult,
    WorkflowForHumanReview,
    EmailExecution,
)
from django.utils import timezone
from agent.models import Agent


def create_human_review_node(state: EmailWorkflowState) -> EmailWorkflowState:

    user = User.objects.get(id=state["user_id"])
    agent = Agent.objects.get(id=state.get("agent_id"))

    WorkflowForHumanReview.objects.create(
        email_body=state.get("raw_email").get("body", ""),
        reply_body=state.get("reply_body", ""),
        reply_subject=state.get("reply_subject", ""),
        user=user,
        sender=state.get("raw_email").get("from"),
        reason=state.get("reason_for_review", ""),
    )

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
    email_execution.result = "HUMAN_REVIEW"
    email_execution.review_reason = state.get("reason_for_review", "")
    email_execution.processed_at = timezone.now()

    email_execution.save()

    exeution = WorkflowExecution.objects.get(id=state.get("execution_id"))
    exeution.status = "SUCCESS"
    exeution.ended_at = timezone.now()
    exeution.save(update_fields=["status", "ended_at"])

    EmailExecutionResult.objects.create(
        agent=agent,
        workflow_execution=exeution,
        email_id=state.get("email_id"),
        result="HUMAN_REVIEW",
    )

    return state

  