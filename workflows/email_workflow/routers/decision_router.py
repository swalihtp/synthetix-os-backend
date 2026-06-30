from workflows.models import WorkflowExecution
from django.utils import timezone


def decision_router(state):
    if state["requires_human"] or state["confidence"] < 0.75:
        state["reason_for_review"] = "Agent is not confident to reply"

        exeution = WorkflowExecution.objects.get(id=state.get("execution_id"))
        exeution.status = "SUCCESS"
        exeution.ended_at = timezone.now()
        exeution.save(update_fields=["status", "ended_at"])

        return "human_review"

    return "send_reply"
