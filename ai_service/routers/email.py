import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm import chat
from services.prompt_builder import (
    email_analysis_prompt,
    reply_generation_prompt,
)

router = APIRouter(prefix="/email", tags=["email"])


class AnalyzeRequest(BaseModel):
    email_body: str
    subject: str = ""


class ReplyRequest(BaseModel):
    email_body: str
    intent: str = "general"
    tone: str = "professional"


@router.post("/analyze")
async def analyze_email(request: AnalyzeRequest):
    try:
        raw = chat(
            system_prompt=email_analysis_prompt(),
            user_message=f"Subject: {request.subject}\n\n{request.email_body}",
            json_mode=True,
        )
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reply")
async def generate_reply(request: ReplyRequest):
    try:
        raw = chat(
            system_prompt=reply_generation_prompt(request.tone),
            user_message=(
                f"Original email:\n{request.email_body}\n\n"
                f"Detected intent: {request.intent}\n\n"
                f"Write a {request.tone} reply."
            ),
            json_mode=True,
        )
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))