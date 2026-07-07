import uuid

from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState

def initialize_node(state: MeetingWorkflowState) -> MeetingWorkflowState:
    print('INITIAL NODE')
    """
    Set up execution context.
    Preserves the execution_id passed in by the caller when available and resets downstream fields
    so re-runs on the same state don't carry stale data.
    """
    return {
        **state,
        "execution_id": state.get("execution_id") or str(uuid.uuid4()),
        "raw_transcript": None,
        "extraction_error": None,
        "topics": None,
        "decisions": None,
        "action_items": None,
        "meeting_summary": None,
        "stored": False,
    }
