import httpx
from django.conf import settings
from .base import BaseAction


def call_ai_service(endpoint: str, payload: dict) -> dict:
    try:
        response = httpx.post(
            f"{settings.AI_SERVICE_URL}{endpoint}",
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise Exception(f"AI service unreachable: {e}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"AI service error: {e.response.text}")


class AnalyzeEmailAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        result = call_ai_service("/email/analyze", {
            "email_body": context.get("email_body", ""),
            "subject": context.get("subject", ""),
        })
        return {"analysis": result}


class ClassifyIntentAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        result = call_ai_service("/intent/detect", {
            "text": context.get("email_body", ""),
            "detect": config.get("detect", ["meeting", "complaint", "general"]),
        })
        return {"intent": result.get("intent", "general")}


class GenerateReplyAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        email_body = context.get("email_body", "")

        if not email_body:
            return {
                "reply_text": "Thank you for your email. I will get back to you shortly."
            }

        result = call_ai_service("/email/reply", {
            "email_body": email_body,
            "intent": context.get("intent", "general"),
            "tone": config.get("tone", "professional"),
        })

        reply = result.get("reply", "")
        if not reply:
            reply = "Thank you for reaching out. I will get back to you as soon as possible."

        return {"reply_text": reply}


class ExtractContentAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        result = call_ai_service("/social/extract", {
            "raw_text": context.get("raw_text", ""),
        })
        return {
            "topic": result.get("topic"),
            "tone": result.get("tone"),
            "key_points": result.get("key_points", []),
        }


class AdaptForPlatformAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        platform = config.get("platform", "twitter")
        result = call_ai_service("/social/adapt", {
            "content": context,
            "platform": platform,
            "config": config,
        })
        return {f"{platform}_post": result.get("adapted_text", "")}


class DetectMeetingIntentAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        result = call_ai_service("/intent/detect", {
            "text": context.get("email_body", ""),
            "detect": ["meeting_request"],
        })
        return {"meeting_intent": result.get("intent") == "meeting_request"}