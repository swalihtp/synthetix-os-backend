import os

import requests
from dotenv import load_dotenv

load_dotenv()


def _normalize_raw_text(raw_text):
    if isinstance(raw_text, str):
        return raw_text

    if isinstance(raw_text, list):
        parts = []
        for item in raw_text:
            if isinstance(item, dict):
                content = item.get("content", "")
                if content:
                    parts.append(content)
            elif isinstance(item, str) and item:
                parts.append(item)
        return "\n\n".join(parts)

    if isinstance(raw_text, dict):
        content = raw_text.get("content")
        if isinstance(content, str):
            return content

    return "" if raw_text is None else str(raw_text)


def analyze_resume(raw_text, job_title=None, job_description=None, file_type=None):
    payload = {
        "raw_text": _normalize_raw_text(raw_text),
        "job_title": job_title,
        "job_description": job_description,
        "file_type": file_type,
    }

    try:
        response = requests.post(
            f'{os.getenv("AI_SERVICE_URL")}/api/analyze-resume',
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    except requests.Timeout:
        raise Exception("AI service timeout")

    except requests.RequestException as exc:
        raise Exception(f"AI service error: {str(exc)}")
