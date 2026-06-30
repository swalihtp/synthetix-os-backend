import os

import requests
from dotenv import load_dotenv

load_dotenv()


def analyze_meeting_notes(raw_transcript, file_type=None, summary_style=None):
    payload = {
        "raw_transcript": raw_transcript or "",
        "file_type": file_type,
        "summary_style": summary_style,
    }

    try:
        response = requests.post(
            f'{os.getenv("AI_SERVICE_URL")}/api/generate-meeting-summary',
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()

    except requests.Timeout:
        raise Exception("AI service timeout")

    except requests.RequestException as exc:
        raise Exception(f"AI service error: {str(exc)}")
