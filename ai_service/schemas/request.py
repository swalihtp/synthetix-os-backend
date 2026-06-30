from pydantic import BaseModel
from typing import Dict, Any


class ExecuteRequest(BaseModel):

    task: str
    payload: Dict[str, Any]
