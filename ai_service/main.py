import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import email, intent, workflow, social

app = FastAPI(
    title="Synthetix OS — AI Service",
    description="AI microservice for intent detection, workflow generation, and content processing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email.router)
app.include_router(intent.router)
app.include_router(workflow.router)
app.include_router(social.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-service"}