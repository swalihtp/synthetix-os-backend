from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


def load_service_env() -> None:
    """
    Load AI service environment variables from both the local service
    directory and the repository root.

    The local file keeps FastAPI-specific values close to the AI service,
    while the repository-level .env remains a convenient fallback during
    monorepo development.
    """

    service_root = Path(__file__).resolve().parents[1]
    repo_root = service_root.parent

    load_dotenv(service_root / ".env", override=False)
    load_dotenv(repo_root / ".env", override=False)


def get_env(name: str, default: str | None = None) -> str | None:
    load_service_env()
    return os.getenv(name, default)


def get_openrouter_api_key() -> str | None:
    return get_env("OPEN_ROUTER_API_KEY") or get_env("OPENAI_API_KEY")


def get_google_api_key() -> str | None:
    return get_env("GOOGLE_API_KEY")

def get_model():
    return get_env("MODEL_NAME")
