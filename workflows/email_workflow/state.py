from typing import TypedDict, Optional, List, Dict


class EmailWorkflowState(TypedDict):
    
    agent_id: str
    email_id: str
    user_id: int
    execution_id: str
    email_execution_id: str
    
    raw_email: dict
    cleaned_email: dict

    attachments: List[dict]

    extracted_documents: List[dict]

    classification: str
    
    confidence: float

    priority: str

    detected_tools: List[str]

    ai_response: Optional[str]

    requires_human: bool
    
    reply_subject: str
    
    reply_body: str

    approved: bool

    actions: List[dict]

    skip_workflow: bool

    metadata: Dict
    
    ai_reply_categories: List[str]
    
    human_review_categories: List[str]
    
    ignore_categories: List[str]
    
    intention: Dict
    
    reason_for_review: str
    
    
    
    
    
    
