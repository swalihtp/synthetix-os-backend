from pydantic import BaseModel
from typing import Any


class ExecuteResponse(BaseModel):

    success: bool

    task: str

    data: Any
