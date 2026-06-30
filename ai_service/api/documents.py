import logging
import uuid
import re

from fastapi import APIRouter, HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from services.email_agent.retreiver import vector_store, embeddings


def clean_text(text: str) -> str:
    text = re.sub(r"[\x00-\x1F\x7F]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


class DocumentPayload(BaseModel):
    document_id: str
    filename: str | None = None
    content: str


class IngestRequest(BaseModel):
    agent_id: str
    user_id: str
    documents: list[DocumentPayload]


@router.post("/ingest")
async def ingest_documents(payload: IngestRequest):
    total_chunks = 0

    try:
        for document in payload.documents:
            if not document.content.strip():
                continue

            content = clean_text(document.content)
            chunks = splitter.split_text(content)
            chunks = [clean_text(chunk) for chunk in chunks if clean_text(chunk)]

            if not chunks:
                continue

            total_chunks += len(chunks)

            # embed_documents() is broken for this model in the installed
            # langchain_google_genai version: it collapses N input texts
            # into a single merged embedding instead of N separate vectors.
            # Looping embed_query() per chunk avoids that bug — confirmed
            # working via direct testing against the raw Google SDK.
            chunk_embeddings = [embeddings.embed_query(chunk) for chunk in chunks]

            if len(chunk_embeddings) != len(chunks):
                raise ValueError(
                    f"Embedding count mismatch: {len(chunks)} chunks, "
                    f"{len(chunk_embeddings)} embeddings returned"
                )

            chunk_ids = [str(uuid.uuid4()) for _ in chunks]
            chunk_metadatas = [
                {
                    "agent_id": payload.agent_id,
                    "user_id": payload.user_id,
                    "document_id": document.document_id,
                    "filename": document.filename or "",
                }
                for _ in chunks
            ]

            # vector_store.add_texts() has no way to accept precomputed
            # embeddings, so we write directly to the underlying Chroma
            # collection instead, bypassing the LangChain wrapper's
            # internal (buggy) re-embedding call entirely.
            vector_store._collection.add(
                documents=chunks,
                embeddings=chunk_embeddings,
                ids=chunk_ids,
                metadatas=chunk_metadatas,
            )

        return {
            "success": True,
            "agent_id": payload.agent_id,
            "documents_processed": len(payload.documents),
            "chunks_created": total_chunks,
        }

    except Exception as exc:
        logger.exception("Document ingestion failed")
        raise HTTPException(status_code=500, detail=str(exc))