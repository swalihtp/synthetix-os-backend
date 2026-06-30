from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState


def can_extract_router(state: MeetingWorkflowState) -> str:
    """Route to analysis if transcript was extracted; otherwise end early."""
    if state.get("raw_transcript"):
        return "continue"
    return "end"
