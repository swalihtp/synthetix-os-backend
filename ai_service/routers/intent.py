import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.llm import chat
from services.prompt_builder import intent_detection_prompt

router = APIRouter(prefix="/intent", tags=["intent"])


class IntentRequest(BaseModel):
    text: str
    detect: List[str] = ["meeting_request", "complaint", "general"]


@router.post("/detect")
async def detect_intent(request: IntentRequest):
    try:
        raw = chat(
            system_prompt=intent_detection_prompt(request.detect),
            user_message=request.text,
            json_mode=True,
        )
        return json.loads(raw)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))