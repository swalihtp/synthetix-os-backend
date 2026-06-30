from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState


def decision_extraction_node(state: MeetingWorkflowState) -> MeetingWorkflowState:
    """
    Deprecated compatibility node.
    Decision extraction now happens inside generate_meeting_summary_node.
    """
    return state
