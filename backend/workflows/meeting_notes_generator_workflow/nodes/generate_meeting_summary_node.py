from django.utils import timezone

from workflows.meeting_notes_generator_workflow.services.ai.ai_service import (
    analyze_meeting_notes,
)
from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState
from workflows.models import AIUsageLog, WorkflowExecution

def generate_meeting_summary_node(state: MeetingWorkflowState) -> MeetingWorkflowState:
    """
    Pipeline task: ai.generate_meeting_summary
    Runs the single bundled LLM call for topics, decisions, action items,
    and the final meeting summary.
    """
    analysis = analyze_meeting_notes(
        raw_transcript=state.get("raw_transcript", ""),
        file_type=state.get("file_type"),
        summary_style=state.get("summary_style"),
    )

    summary = {
        **analysis["meeting_summary"],
        "topics_discussed": analysis["topics"],
        "decisions": analysis["decisions"],
        "action_items": analysis["action_items"],
        "execution_id": state["execution_id"],
        "summary_style": state.get("summary_style"),
        "generated_at": timezone.now().isoformat(),
    }
    execution = WorkflowExecution.objects.get(id=state.get("execution_id"))
    
    AIUsageLog.objects.create(
        workflow_execution=execution,
        provider="OPENROUTER",
        model_name="poolside/laguna-xs-2.1:free",
        operation="MEETING_SUMMARY",
    )
    return {
        **state,
        "topics": analysis["topics"],
        "decisions": analysis["decisions"],
        "action_items": analysis["action_items"],
        "meeting_summary": summary,
    }
