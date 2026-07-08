from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import time
import traceback
import json

from services.env import get_openrouter_api_key

router = APIRouter()


# REQUEST / RESPONSE MODELS


class AnalyzeIntentRequest(BaseModel):
    subject: str
    email_body: str
    intentions: list[str]


class AnalyzeIntentResponse(BaseModel):
    intention: str
    confidence: float = Field(ge=0, le=1)
    reason: str


# LLM


llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0,
    api_key=get_openrouter_api_key(),
    base_url="https://openrouter.ai/api/v1",
    timeout=60,
    max_retries=2,
)


# PROMPT

system_prompt = """
You are an email intent classification engine.

You MUST select EXACTLY ONE intention from the provided intentions.

Rules:

1. Only choose from the provided intentions.
2. Never invent a new intention.
3. Analyze:
   - subject
   - body
   - sender intent
   - urgency
   - business context
4. If uncertain choose the closest intention.
5. Confidence must be between 0 and 1.

Return ONLY valid JSON.

Example:

{{
  "intention": "Customer Support",
  "confidence": 0.92,
  "reason": "Customer is requesting help with a product issue."
}}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        (
            "human",
            """
Available Intentions:
{intentions}

Email Subject:
{subject}

Email Body:
{email_body}
""",
        ),
    ]
)

chain = prompt | llm


# FALLBACK LOGIC


def fallback_intent(intentions: list[str]) -> AnalyzeIntentResponse:
    """
    Used when the LLM completely fails.
    """

    default_intent = intentions[0] if intentions else "Unknown"

    return AnalyzeIntentResponse(
        intention=default_intent,
        confidence=0.1,
        reason="Fallback response because LLM output could not be parsed.",
    )


# NORMALIZE HELPER


def normalize(s: str) -> str:
    return s.strip().lower()


# ANALYZE


async def analyze_intention( payload: AnalyzeIntentRequest) -> AnalyzeIntentResponse:

    start = time.time()

    try:

        response = await chain.ainvoke(
            {
                "intentions": "\n".join(payload.intentions),
                "subject": payload.subject,
                "email_body": payload.email_body,
            }
        )

        print(f"LLM took {time.time() - start:.2f}s")

        raw_content = response.content.strip()

        print("RAW RESPONSE:")
        print(raw_content)

        # remove markdown fences
        raw_content = raw_content.replace("```json", "")
        raw_content = raw_content.replace("```", "")
        raw_content = raw_content.strip()

        data = json.loads(raw_content)

        intention = data.get("intention", "")
        confidence = float(data.get("confidence", 0))
        reason = data.get("reason", "")

        # normalize both sides to handle casing/whitespace mismatches
        normalized_map = {normalize(i): i for i in payload.intentions}
        matched = normalized_map.get(normalize(intention))

        if not matched:
            print(f"Invalid intention returned: '{intention}'")
            print(f"Available intentions: {payload.intentions}")
            return fallback_intent(payload.intentions)

        # use the original casing from the intentions list
        intention = matched

        confidence = max(0.0, min(confidence, 1.0))

        return AnalyzeIntentResponse(
            intention=intention,
            confidence=confidence,
            reason=reason,
        )

    except Exception as e:

        print("ANALYZE INTENTION ERROR")
        traceback.print_exc()

        return fallback_intent(payload.intentions)


# API
@router.post(
    "/analyze-intention",
    response_model=AnalyzeIntentResponse,
)
async def analyze_intention_endpoint(
    payload: AnalyzeIntentRequest,
):
    print("REQUEST RECEIVED INTO AI SERVICE")
    print(f"PAYLOAD:{payload}")
    try:
        return await analyze_intention(payload)

    except Exception as e:

        print("ENDPOINT ERROR")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
