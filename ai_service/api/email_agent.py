from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.email_agent.llm import llm
from services.email_agent.retreiver import (
    compony_knowledge_retriever,
    memory_vector_store,
)
from services.email_agent.schemas import EmailAgentResponse
from services.email_agent.prompt import SYSTEM_PROMPT

router = APIRouter()

structured_llm = llm.with_structured_output(EmailAgentResponse)


class AIServiceRequest(BaseModel):
    raw_email: dict
    extracted_documents: list[str] = Field(default_factory=list)
    user_id: str
    message_id: str
    user_context: dict


@router.post("/process-email")
async def ai_service(state: AIServiceRequest):
    

    try:
        raw_email = state.raw_email
        extracted_documents = state.extracted_documents

        subject = raw_email.get("subject", "")
        body = raw_email.get("body", "")

        retrieval_query = f"""
            Subject: {subject}

            Body:
            {body}
        """

        thread_retriever = memory_vector_store.as_retriever(
            search_kwargs={
                "k": 8,
                "filter": {
                    "$and": [
                        {"user_id": state.user_id},
                        {"thread_id": state.raw_email.get('thread_id')},
                    ]
                },
            }
        )
        
        sender_retriever = memory_vector_store.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {
                    "$and": [
                        {"user_id": state.user_id},
                        {"sender_email": state.raw_email.get('from')},
                    ]
                },
            }
        )

        company_knowledge_retrieved_docs = compony_knowledge_retriever.invoke(
            retrieval_query
        )
        thread_docs = thread_retriever.invoke(retrieval_query)
        sender_docs = sender_retriever.invoke(retrieval_query)
        
        print(f"-----THREAD DOC:{thread_docs}")
        
        print(f"-----SENDER DOC:{sender_docs}")

        company_context = "\n\n".join(
            [doc.page_content for doc in company_knowledge_retrieved_docs]
        )


        thread_context = "\n\n".join(
            [doc.page_content for doc in thread_docs]
        )
        
        thread_message_ids = {
            doc.metadata.get("message_id")
            for doc in thread_docs
        }

        sender_docs = [
            doc for doc in sender_docs
            if doc.metadata.get("message_id") not in thread_message_ids
        ]

        sender_context = "\n\n".join(
            [doc.page_content for doc in sender_docs]
        )
        
        extracted_context = "\n\n".join(extracted_documents)

        final_prompt = f"""
            {SYSTEM_PROMPT}

            EMAIL:
            Subject: {subject}

            Body:
            {body}
            
            ATTACHED DOCUMENTS:
            {extracted_context}

            COMPANY KNOWLEDGE:
            {company_context}

            THREAD CONVERSATION HISTORY:
            {thread_context}

            SENDER RELATIONSHIP MEMORY:
            {sender_context}

        
            USER INFORMATION:
            Name: {state.user_context.get("name","")}
            Email: {state.user_context.get("email")}

            IMPORTANT:
            - Never use placeholders
            - Sign naturally using the user name
            
            IMPORTANT MEMORY RULES:
            - Prefer ATTACHED DOCUMENT and  THREAD CONVERSATION HISTORY over sender memory
            - Use sender memory only for communication style and long-term relationship context
            - Do not repeat old information unnecessarily
            - Maintain continuity with the current thread
            
            
        """

        response = structured_llm.invoke(final_prompt)

        return response.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
