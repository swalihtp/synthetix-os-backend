from workflows.resume_analyzer_workflow.state import ResumeWorkflowState


def can_extract_router(state: ResumeWorkflowState) -> str:
    """Route to analysis if text was extracted; otherwise end early."""
    if state.get("raw_text"):
        return "continue"
    return "end"
