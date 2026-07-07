from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState


def topic_detection_node(state: MeetingWorkflowState) -> MeetingWorkflowState:
    """
    Deprecated compatibility node.
    Topic detection now happens inside generate_meeting_summary_node.
    """
    return state
