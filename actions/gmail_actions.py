from .base import BaseAction
from integrations.models import Integration


def get_gmail_client(user_id):
    """Fetch stored OAuth token for Gmail."""
    try:
        integration = Integration.objects.get(
            user_id=user_id,
            provider='gmail',
            is_active=True
        )
        return integration
    except Integration.DoesNotExist:
        raise Exception("Gmail not connected. Please connect Gmail first.")


class GmailFetchEmailAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        # Stub — will use Gmail API with OAuth token
        # For now returns context as-is (webhook already has email data)
        return {
            "email_body": context.get("payload", {}).get("body", ""),
            "subject": context.get("payload", {}).get("subject", ""),
            "sender": context.get("payload", {}).get("from", ""),
            "thread_id": context.get("payload", {}).get("thread_id", ""),
        }


class GmailSendReplyAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        # Stub — will call Gmail API
        reply_text = context.get("reply_text", "")
        thread_id = context.get("thread_id", "")
        print(f"[STUB] Sending Gmail reply to thread {thread_id}: {reply_text[:50]}...")
        return {"reply_sent": True, "thread_id": thread_id}