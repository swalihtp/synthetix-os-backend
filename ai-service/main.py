from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import email_agent
from api import store_doc
from api import market_agent
from api import summarization
from api import analyze_intentions
from api import execute
from api import documents
from api import resume_analysis
from api import meeting_notes

app = FastAPI(
    title="Synthetix AI Service",
    description="AI microservice for email processing and automation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(email_agent.router, prefix="/api")
app.include_router(store_doc.router, prefix="/api")
app.include_router(market_agent.router, prefix="/api/market-inteligence")
app.include_router(summarization.router, prefix="/api")
app.include_router(analyze_intentions.router, prefix="/api")
app.include_router(execute.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(resume_analysis.router, prefix="/api")
app.include_router(meeting_notes.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
