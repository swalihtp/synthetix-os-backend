from typing import TypedDict, Optional

class ResumeWorkflowState(TypedDict):
    # Input
    file_path: str                        # Path / URL to the uploaded resume file
    file_type: str                        # "pdf" | "docx" | "txt"
    job_title: Optional[str]              # Target role title from the request payload
    job_description: Optional[str]        # Target role description from the request payload
 
    # Ingestion
    raw_text: Optional[str]               # Extracted plain text from the resume
    extraction_error: Optional[str]       # Set if extraction fails
 
    # Analysis outputs
    resume_analysis: Optional[dict]       # Structure, clarity, formatting findings
    skill_evaluation: Optional[dict]      # Matched skills, gaps, keyword hits
    ats_score: Optional[dict]             # ATS compatibility score + breakdown
 
    # Output
    feedback_report: Optional[dict]       # Final structured report delivered to user
 
    # Memory / persistence
    execution_id: Optional[str]           # Unique run ID stored in Postgres
    stored: bool
    resume_execution_id: Optional[str]
