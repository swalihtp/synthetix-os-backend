from pathlib import Path
from django.utils import timezone
from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState
from workflows.models import MeetingSummaryExecution, WorkflowExecution
from workflows.utils.realtime import send_workflow_update


def store_summary_node(state: MeetingWorkflowState) -> MeetingWorkflowState:
    """
    Persist the full meeting summary to Postgres (long-term execution history).
    """
    print("LAST SUMMARY NODE")
    workflow_execution = WorkflowExecution.objects.get(id=state["execution_id"])
    meeting_execution, _ = MeetingSummaryExecution.objects.get_or_create(
        workflow_execution=workflow_execution,
        defaults={
            "file_name": Path(state["file_path"]).name,
            "file_type": state.get("file_type"),
            "file_path": state["file_path"],
            "summary_style": state.get("summary_style"),
            "status": "processing",
        },
    )

    meeting_execution.file_name = meeting_execution.file_name or Path(
        state["file_path"]
    ).name
    meeting_execution.file_type = state.get("file_type") or meeting_execution.file_type
    meeting_execution.file_path = state["file_path"]
    meeting_execution.summary_style = state.get("summary_style") or meeting_execution.summary_style
    meeting_execution.status = "completed"
    meeting_execution.error_message = None
    meeting_execution.raw_transcript = state.get("raw_transcript")
    meeting_execution.topics = state.get("topics")
    meeting_execution.decisions = state.get("decisions")
    meeting_execution.action_items = state.get("action_items")
    meeting_execution.meeting_summary = state.get("meeting_summary")
    meeting_execution.save(
        update_fields=[
            "file_name",
            "file_type",
            "file_path",
            "summary_style",
            "status",
            "error_message",
            "raw_transcript",
            "topics",
            "decisions",
            "action_items",
            "meeting_summary",
        ]
    )

    workflow_execution.status = "SUCCESS"
    workflow_execution.ended_at = timezone.now()
    workflow_execution.error_message = None
    workflow_execution.save(update_fields=["status", "ended_at", "error_message"])

    send_workflow_update(
        workflow_execution.workflow.agent_id,
        {
            "event": "meeting_notes_completed",
            "workflow_execution_id": str(workflow_execution.id),
            "meeting_execution_id": str(meeting_execution.id),
            "status": "completed",
            "message": "Meeting notes analysis completed",
        },
    )

    print(f"[store_summary] Saving execution {state['execution_id']} to Postgres")
    return {**state, "stored": True}
