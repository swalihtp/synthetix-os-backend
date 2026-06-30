from workflows.resume_analyzer_workflow.state import ResumeWorkflowState

def initialize_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Set up execution context.
    Generates a unique execution_id, validates the incoming state,
    and prepares any agent-level config (model, temperature, etc.).
    """

    return {
        **state,
        "raw_text": None,
        "extraction_error": None,
        "resume_analysis": None,
        "skill_evaluation": None,
        "ats_score": None,
        "feedback_report": None,
        "stored": False,
    }
