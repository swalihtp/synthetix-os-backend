from typing import TypedDict, Optional, List


class MeetingWorkflowState(TypedDict):
    # Input
    file_path: str  # Path / URL to transcript file
    file_type: str  # "txt" | "pdf" | "docx" | "vtt" | "srt"
    summary_style: Optional[str]  # "concise" | "detailed" | "executive"

    # Ingestion
    raw_transcript: Optional[str]  # Raw extracted text from the file
    extraction_error: Optional[str]  # Set if extraction fails

    # Analysis outputs
    topics: Optional[List[dict]]  # Detected topics with speaker refs
    decisions: Optional[List[dict]]  # Decisions made during the meeting
    action_items: Optional[List[dict]]  # Action items with owner + due date

    # Output
    meeting_summary: Optional[dict]  # Final structured meeting report

    # Memory / persistence
    execution_id: Optional[str]  # Unique run ID stored in Postgres
    stored: bool  # True once summary is persisted
