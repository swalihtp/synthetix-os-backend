from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.llm_service import llm
import time

router = APIRouter()


class ResumeAnalysisRequest(BaseModel):
    raw_text: str
    job_title: str | None = None
    job_description: str | None = None
    file_type: str | None = None


class ResumeAnalysisResponse(BaseModel):
    sections_found: list[str]
    missing_sections: list[str]
    formatting_issues: list[str]
    clarity_score: float = Field(ge=0, le=1)


class SkillEvaluationResponse(BaseModel):
    extracted_skills: list[str]
    skill_gaps: list[str]
    keyword_hits: int
    keyword_misses: list[str]


class AtsScoringResponse(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    parse_friendly: bool
    issues: list[str]
    recommended_format: str


class FeedbackReportResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    summary: str
    priority_actions: list[str]
    section_feedback: dict[str, str]
    ats_tips: list[str]


class ResumeAnalysisBundleResponse(BaseModel):
    resume_analysis: ResumeAnalysisResponse
    skill_evaluation: SkillEvaluationResponse
    ats_score: AtsScoringResponse
    feedback_report: FeedbackReportResponse


structured_llm = llm.with_structured_output(ResumeAnalysisBundleResponse)

SYSTEM_PROMPT_FOR_RESUME_ANALYSIS = """
You are an expert resume analysis assistant.

Your responsibilities:
1. Analyze resume structure, formatting, section completeness, and clarity.
2. Extract the most relevant skills from the resume.
3. Score ATS compatibility from 0 to 100.
4. Produce a concise feedback report with prioritized actions.
5. Return structured data only.

Rules:
- Use only the provided resume text and optional job context
- Do not hallucinate missing sections, skills, or formatting problems
- clarity_score must be between 0 and 1
- ats_score must be an integer between 0 and 100
- priority_actions must be ordered by impact
"""


@router.post("/analyze-resume")
async def analyze_resume(state: ResumeAnalysisRequest):

    print(len(state.raw_text))

    try:
        start = time.time()
        print("Request received")
        final_prompt = f"""
{SYSTEM_PROMPT_FOR_RESUME_ANALYSIS}

JOB TITLE:
{state.job_title or ""}

JOB DESCRIPTION:
{state.job_description or ""}

FILE TYPE:
{state.file_type or ""}

RESUME TEXT:
{state.raw_text}
"""
        print(final_prompt[:500])
        print(f"Prompt built in {time.time() - start:.2f}s")
        t = time.time()
        response = structured_llm.invoke(final_prompt)
        print(f"Total {time.time() - start:.2f}s")
        return response.model_dump()

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
