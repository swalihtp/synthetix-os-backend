from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.market_agent.llm import llm

from services.market_agent.schemas import (
    CompetitorAnalysisResponse,
    MarketResearchResponse,
    TrendAnalysisResponse,
    SentimentAnalysisResponse,
    SWOTAnalysisResponse,
    ReportGenerationResponse,
    PlannerResponse,
)

from services.market_agent.prompt import (
    SYSTEM_PROMPT_FOR_COMPETITOR_ANALYSIS,
    SYSTEM_PROMPT_FOR_MARKET_RESEARCH,
    SYSTEM_PROMPT_FOR_TREND_ANALYSIS,
    SYSTEM_PROMPT_FOR_SENTIMENT_ANALYSIS,
    SYSTEM_PROMPT_FOR_SWOT_ANALYSIS,
    SYSTEM_PROMPT_FOR_REPORT_GENERATION,
    SYSTEM_PROMPT_FOR_PLANNER,
)

router = APIRouter()


class MarketAgentRequest(BaseModel):
    prompt: str
    context: str | None = None
    competitors_data_from_scraping:str | None


planner_llm = llm.with_structured_output(PlannerResponse)


@router.post("/generate-plan")
async def generate_plan(state: MarketAgentRequest):
    print("user prompt in generate reply", state.prompt)
    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_PLANNER}

        USER PROMPT:
        {state.prompt}
        """

        response = planner_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


market_llm = llm.with_structured_output(MarketResearchResponse)


@router.post("/analyze-market")
async def analyze_market(state: MarketAgentRequest):
    print('analyze market context::', state.context)
    print('analyze market prompt::', state.prompt)
    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_MARKET_RESEARCH}

        CONTEXT:
        {state.context}

        USER PROMPT:
        {state.prompt}
        """

        response = market_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


competitor_llm = llm.with_structured_output(CompetitorAnalysisResponse)
@router.post("/analyze-competitors")
async def analyze_competitors(state: MarketAgentRequest):

    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_COMPETITOR_ANALYSIS}

        CONTEXT:
        {state.context}

        USER PROMPT:
        {state.prompt}
        
        COMPETITORS_DATA FROM THEIR WEBSITES:
        {state.competitors_data_from_scraping}
        """

        response = competitor_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


trend_llm = llm.with_structured_output(TrendAnalysisResponse)
@router.post("/analyze-trends")
async def analyze_trends(state: MarketAgentRequest):
    print('analyze trend', state.context)
    print('analyze trend', state.prompt)
    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_TREND_ANALYSIS}

        CONTEXT:
        {state.context}

        USER PROMPT:
        {state.prompt}
        """

        response = trend_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


sentiment_llm = llm.with_structured_output(SentimentAnalysisResponse)
@router.post("/analyze-sentiment")
async def analyze_sentiment(state: MarketAgentRequest):
    print('analyze sentiment',state.context)
    print('analyze sentiment',state.prompt)
    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_SENTIMENT_ANALYSIS}

        CONTEXT:
        {state.context}

        USER PROMPT:
        {state.prompt}
        """

        response = sentiment_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


swot_llm = llm.with_structured_output(SWOTAnalysisResponse)
@router.post("/analyze-swot")
async def analyze_swot(state: MarketAgentRequest):
    print('analyze swot', state.context)
    print('analyze swot', state.prompt)
    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_SWOT_ANALYSIS}

        CONTEXT:
        {state.context}

        USER PROMPT:
        {state.prompt}
        """

        response = swot_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


report_llm = llm.with_structured_output(ReportGenerationResponse)
@router.post("/generate-report")
async def generate_report(state: MarketAgentRequest):
    print('generate- replay', state.prompt)
    try:
        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_REPORT_GENERATION}

        CONTEXT:
        {state.prompt}
        """

        response = report_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
