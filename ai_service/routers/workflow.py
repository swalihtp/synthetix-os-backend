import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm import chat
from services.prompt_builder import workflow_generation_prompt

router = APIRouter(prefix="/workflow", tags=["workflow"])


class WorkflowGenerateRequest(BaseModel):
    prompt: str


@router.post("/generate")
async def generate_workflow(request: WorkflowGenerateRequest):
    try:
        raw = chat(
            system_prompt=workflow_generation_prompt(),
            user_message=(
                f"User goal: {request.prompt}\n\n"
                f"Generate a complete workflow JSON for this goal."
            ),
            json_mode=True,
        )
        result = json.loads(raw)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))