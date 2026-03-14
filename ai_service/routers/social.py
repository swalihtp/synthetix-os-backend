import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm import chat
from services.prompt_builder import (
    social_extract_prompt,
    social_adapt_prompt,
)

router = APIRouter(prefix="/social", tags=["social"])


class ExtractRequest(BaseModel):
    raw_text: str


class AdaptRequest(BaseModel):
    content: dict
    platform: str
    config: dict = {}


@router.post("/extract")
async def extract_content(request: ExtractRequest):
    try:
        raw = chat(
            system_prompt=social_extract_prompt(),
            user_message=request.raw_text,
            json_mode=True,
        )
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adapt")
async def adapt_content(request: AdaptRequest):
    try:
        raw_text = request.content.get("raw_text", "")
        topic = request.content.get("topic", "")
        key_points = request.content.get("key_points", [])

        user_message = (
            f"Content to adapt:\n{raw_text}\n\n"
            f"Topic: {topic}\n"
            f"Key points: {', '.join(key_points) if key_points else 'N/A'}\n\n"
            f"Adapt this for {request.platform}."
        )

        raw = chat(
            system_prompt=social_adapt_prompt(request.platform),
            user_message=user_message,
            json_mode=True,
        )
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))