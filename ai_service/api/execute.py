from fastapi import APIRouter
from schemas.request import ExecuteRequest
from tasks.company_profile import company_profile_task
from tasks.research_gap import research_gap_task
from tasks.competitor_analysis import competitor_analysis_task
from tasks.market_trends import market_trends_task
from tasks.swot import swot_task
from tasks.recommendations import recommendations_task
from tasks.executive_summary import executive_summary_task
from tasks.market_report import market_report_task
from tasks.profile_enrichment import profile_enrichment_task

router = APIRouter()

TASK_MAP = {
    "company_profile": company_profile_task,
    "research_gap_detection": research_gap_task,
    "competitor_analysis": competitor_analysis_task,
    "market_trends": market_trends_task,
    "swot": swot_task,
    "recommendations": recommendations_task,
    "executive_summary": executive_summary_task,
    "market_report": market_report_task,
    "profile_enrichment": profile_enrichment_task,
}


@router.post("/execute")
async def execute(request: ExecuteRequest):
    
    task = request.task

    if task not in TASK_MAP:

        return {"success": False, "error": f"Unknown task {task}"}

    result = TASK_MAP[task](request.payload)

    return {"success": True, "task": task, "data": result}
