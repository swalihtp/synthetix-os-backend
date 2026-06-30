from workflows.resume_analyzer_workflow.state import ResumeWorkflowState
from workflows.resume_analyzer_workflow.services.ai.ai_service import analyze_resume


def resume_analysis_node(state: ResumeWorkflowState) -> ResumeWorkflowState:
    """
    Pipeline task: ai.resume_analysis_bundle
    Runs the single LLM call for structure, skill extraction, ATS scoring,
    and final feedback generation.
    """
    analysis = analyze_resume(
        raw_text=state.get("raw_text", ""),
        job_title=state.get("job_title"),
        job_description=state.get("job_description"),
        file_type=state.get("file_type"),
    )
    return {
        **state,
        "resume_analysis": analysis["resume_analysis"],
        "skill_evaluation": analysis["skill_evaluation"],
        "ats_score": analysis["ats_score"],
        "feedback_report": analysis["feedback_report"],
    }
