from workflows.resume_analyzer_workflow.state import ResumeWorkflowState


def ats_scoring_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Deprecated compatibility node.
    ATS scoring now happens inside resume_analysis_node.
    """
    return state
