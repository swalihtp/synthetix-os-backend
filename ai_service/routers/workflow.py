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
    print(f"[Workflow Generate] Received prompt: {request.prompt}")
    try:
        raw = chat(
            system_prompt=workflow_generation_prompt(),
            user_message=f"User goal: {request.prompt}",
            json_mode=True,
        )
        print(f"[Workflow Generate] Raw output: {raw[:200]}")
        raw = raw.strip()
        result = json.loads(raw)
        print(f"[Workflow Generate] Parsed successfully")
        return result

    except Exception as e:
        import traceback
        print(f"[Workflow Generate] ERROR: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")