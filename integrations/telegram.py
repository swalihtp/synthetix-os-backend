import os
import httpx


TELEGRAM_API = "https://api.telegram.org"


def send_message(chat_id: str, text: str, parse_mode: str = "HTML") -> dict:
    """Send a message to a Telegram chat."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise Exception("TELEGRAM_BOT_TOKEN not set in environment.")

    response = httpx.post(
        f"{TELEGRAM_API}/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def send_workflow_notification(
    chat_id: str,
    workflow_name: str,
    status: str,
    context: dict,
) -> dict:
    """Send a formatted workflow completion notification."""
    status_emoji = {
        "completed": "✅",
        "failed": "❌",
        "running": "⚙️",
    }.get(status, "ℹ️")

    # Build context summary
    details = []
    if context.get("subject"):
        details.append(f"📧 Subject: {context['subject']}")
    if context.get("intent"):
        details.append(f"🎯 Intent: {context['intent']}")
    if context.get("reply_text"):
        reply_preview = context["reply_text"][:100]
        details.append(f"💬 Reply: {reply_preview}...")
    if context.get("event_created"):
        meeting_time = context.get("meeting_time", "")
        details.append(f"📅 Meeting scheduled: {meeting_time}")
    if context.get("twitter_post"):
        details.append(f"🐦 Twitter post scheduled")
    if context.get("linkedin_post"):
        details.append(f"💼 LinkedIn post scheduled")

    details_text = "\n".join(details) if details else "No details available"

    message = (
        f"{status_emoji} <b>Workflow {status.upper()}</b>\n\n"
        f"<b>{workflow_name}</b>\n\n"
        f"{details_text}"
    )

    return send_message(chat_id, message)