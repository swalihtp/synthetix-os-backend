from workflows.resume_analyzer_workflow.state import ResumeWorkflowState


def generate_feedback_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Deprecated compatibility node.
    Feedback generation now happens inside resume_analysis_node.
    """
    return state
