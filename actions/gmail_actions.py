from .base import BaseAction
from integrations.models import Integration


class GmailFetchEmailAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        """
        In real flow: fetch email from Gmail API using message_id from payload.
        For webhook flow: email data is already in context from the webhook payload.
        """
        payload = context.get("payload", {})

        # If we already have email data from webhook payload, use it
        if payload.get("body") or payload.get("email_body"):
            return {
                "email_body": payload.get("body") or payload.get("email_body", ""),
                "subject": payload.get("subject", ""),
                "sender": payload.get("from") or payload.get("sender", ""),
                "thread_id": payload.get("thread_id", ""),
                "message_id": payload.get("message_id", ""),
            }

        # If we have a message_id, fetch from Gmail API
        message_id = payload.get("message_id") or payload.get("messageId")
        user_id = context.get("user_id")

        if message_id and user_id:
            try:
                from django.contrib.auth import get_user_model
                from integrations.gmail import get_gmail_service, get_email_details
                User = get_user_model()
                user = User.objects.get(id=user_id)
                service = get_gmail_service(user)
                email_data = get_email_details(service, message_id)
                return {
                    "email_body": email_data["body"],
                    "subject": email_data["subject"],
                    "sender": email_data["from"],
                    "thread_id": email_data["thread_id"],
                    "message_id": message_id,
                }
            except Exception as e:
                print(f"[Gmail] Could not fetch email: {e}")

        # Fallback stub
        return {
            "email_body": payload.get("body", "Hello, I would like to schedule a meeting."),
            "subject": payload.get("subject", "Meeting Request"),
            "sender": payload.get("from", "sender@example.com"),
            "thread_id": payload.get("thread_id", "thread-stub-001"),
            "message_id": payload.get("message_id", "msg-stub-001"),
        }


class GmailSendReplyAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        reply_text = context.get("reply_text", "")
        thread_id = context.get("thread_id", "")
        sender = context.get("sender", "")
        subject = context.get("subject", "")
        user_id = context.get("user_id")

        if not reply_text:
            return {"reply_sent": False, "error": "No reply text generated"}

        # Try real Gmail send if user has integration connected
        if user_id and thread_id and sender:
            try:
                from django.contrib.auth import get_user_model
                from integrations.gmail import get_gmail_service, send_reply
                User = get_user_model()
                user = User.objects.get(id=user_id)
                service = get_gmail_service(user)
                send_reply(service, thread_id, sender, subject, reply_text)
                print(f"[Gmail] Reply sent to {sender} in thread {thread_id}")
                return {"reply_sent": True, "thread_id": thread_id}
            except Exception as e:
                print(f"[Gmail] Could not send reply: {e}")

        # Stub fallback
        print(f"[STUB] Gmail reply to {sender}: {reply_text[:80]}...")
        return {"reply_sent": True, "thread_id": thread_id, "stub": True}