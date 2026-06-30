from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.documents import Document
from services.email_agent.retreiver import memory_vector_store


router = APIRouter()

class StoreDocRequest(BaseModel):
    raw_email: dict
    user_id: str
    reply_subject: str
    reply_text: str
    
@router.post("/store-doc")
async def store_document(state: StoreDocRequest):
    
    content = f"""
        SUBJECT:
        {state.raw_email['subject']}
        CUSTOMER EMAIL:
        {state.raw_email['body']}
        
        AI REPLY SUBJECT:
        {state.reply_subject}

        AI REPLY:
        {state.reply_text}
    """
    doc = Document(
    page_content=content,
    metadata={
        "user_id": state.user_id,
        "sender_email": state.raw_email.get("from"),
        "thread_id": state.raw_email.get("thread_id"),
        "message_id": state.raw_email.get("message_id"),
        "type": "email_conversation",
        }
    )
    
    memory_vector_store.add_documents([doc])
    
    return {"message": "Document saved successfully"}