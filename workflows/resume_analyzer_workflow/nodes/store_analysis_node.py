from workflows.resume_analyzer_workflow.state import ResumeWorkflowState
from pathlib import Path

from workflows.models import ResumeExecution, WorkflowExecution
from django.utils import timezone
from workflows.utils.realtime import send_workflow_update


def store_analysis_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Persist the full analysis to Postgres (long-term execution history).
    actions.store_analysis = True in agent config.
    """
    workflow_execution = WorkflowExecution.objects.get(id=state["execution_id"])
    resume_execution, _ = ResumeExecution.objects.get_or_create(
        workflow_execution=workflow_execution,
        defaults={
            "file_name": Path(state["file_path"]).name,
            "file_type": state.get("file_type"),
            "file_path": state["file_path"],
        },
    )

    resume_execution.file_name = resume_execution.file_name or Path(state["file_path"]).name
    resume_execution.file_type = state.get("file_type") or resume_execution.file_type
    resume_execution.file_path = state["file_path"]
    resume_execution.raw_text = state.get("raw_text")
    resume_execution.resume_analysis = state.get("resume_analysis")
    resume_execution.skill_evaluation = state.get("skill_evaluation")
    resume_execution.ats_score = state.get("ats_score")
    resume_execution.feedback_report = state.get("feedback_report")
    resume_execution.status = "completed"
    resume_execution.error_message = None
    resume_execution.save(
        update_fields=[
            "file_name",
            "file_type",
            "file_path",
            "raw_text",
            "resume_analysis",
            "skill_evaluation",
            "ats_score",
            "feedback_report",
            "status",
            "error_message",
        ]
    )

    workflow_execution.status = "SUCCESS"
    workflow_execution.ended_at = timezone.now()
    workflow_execution.error_message = None
    workflow_execution.save(update_fields=["status", "ended_at", "error_message"])

    send_workflow_update(
        workflow_execution.workflow.agent_id,
        {
            "event": "resume_analysis_completed",
            "workflow_execution_id": str(workflow_execution.id),
            "resume_execution_id": str(resume_execution.id),
            "status": "completed",
            "message": "Resume analysis completed",
        },
    )

    print(f"[store_analysis] Saving execution {state['execution_id']} to Postgres")
    return {**state, "stored": True}
