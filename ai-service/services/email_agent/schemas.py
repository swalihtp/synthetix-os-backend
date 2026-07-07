from pydantic import BaseModel
from typing import List


class EmailAgentResponse(BaseModel):
    classification: str
    confidence: float
    priority: str
    requires_human: bool
    reply_subject: str
    reply_body: str
    detected_tools: List[str]