# app/api/routes/summarize.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from langchain_openai import ChatOpenAI
from services.env import get_openrouter_api_key


router = APIRouter()


# =========================================================
# LLM
# =========================================================

base_llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0,
    api_key=get_openrouter_api_key(),
    base_url="https://openrouter.ai/api/v1",
)


# =========================================================
# Request Schema
# =========================================================

class SummarizeRequest(BaseModel):

    content: str

    company: Optional[str] = None


# =========================================================
# Response Schema
# =========================================================

class SummarizeResponse(BaseModel):

    summary: str


# =========================================================
# Structured Output
# =========================================================

llm = base_llm.with_structured_output(
    SummarizeResponse
)


# =========================================================
# Prompt
# =========================================================

SYSTEM_PROMPT_FOR_SUMMARIZATION = """
You are an AI business intelligence summarization assistant.

Your responsibilities:
1. Summarize large business and website content
2. Keep only important insights
3. Remove repetitive or irrelevant information
4. Preserve key business context
5. Keep the summary concise but informative

Rules:
- Do not hallucinate
- Use only provided content
- Focus on business-relevant insights
- Return plain text summary only
"""


# =========================================================
# Endpoint
# =========================================================

@router.post(
    "/summarize",
    response_model=SummarizeResponse
)
async def summarize_content(
    state: SummarizeRequest
):

    try:

        final_prompt = f"""
        {SYSTEM_PROMPT_FOR_SUMMARIZATION}

        COMPANY:
        {state.company}

        CONTENT:
        {state.content}

        Create a concise summary.
        """

        response = llm.invoke(final_prompt)

        return response

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
