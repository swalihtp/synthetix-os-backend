from workflows.resume_analyzer_workflow.state import ResumeWorkflowState


def skill_evaluation_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Deprecated compatibility node.
    Skill evaluation now happens inside resume_analysis_node.
    """
    return state
