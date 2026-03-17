import os
from .base import BaseAction


class SchedulePostsAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        platforms = config.get("platforms", ["twitter", "linkedin", "instagram"])
        scheduled = {}
        for platform in platforms:
            post_text = context.get(f"{platform}_post", "")
            if post_text:
                print(f"[STUB] Scheduling {platform} post: {post_text[:50]}...")
                scheduled[platform] = "scheduled"
        return {"scheduled_posts": scheduled}


class NotifyUserAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        channel = config.get("channel", "telegram")
        message = config.get("message", "")
        user_id = context.get("user_id")

        if channel == "telegram":
            return self._send_telegram(config, context, message, user_id)

        print(f"[STUB] Notifying via {channel}: {message}")
        return {"notification_sent": True, "channel": channel}

    def _send_telegram(self, config, context, message, user_id):
        from integrations.telegram import send_message, send_workflow_notification

        # Get chat_id — from config, context, or env default
        chat_id = (
            config.get("chat_id")
            or context.get("telegram_chat_id")
            or os.environ.get("TELEGRAM_CHAT_ID")
        )

        if not chat_id:
            print("[Telegram] No chat_id found — skipping notification")
            return {"notification_sent": False, "error": "No chat_id"}

        try:
            if message:
                # Send custom message from config
                send_message(str(chat_id), message)
            else:
                # Send workflow summary notification
                send_workflow_notification(
                    chat_id=str(chat_id),
                    workflow_name=context.get("workflow_name", "Workflow"),
                    status="completed",
                    context=context,
                )
            print(f"[Telegram] Notification sent to chat {chat_id}")
            return {"notification_sent": True, "channel": "telegram"}
        except Exception as e:
            print(f"[Telegram] Failed to send: {e}")
            return {"notification_sent": False, "error": str(e)}


class SlackMessageAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        webhook_url = config.get("webhook_url") or os.environ.get("SLACK_WEBHOOK_URL")

        if webhook_url:
            try:
                import httpx
                text = config.get("message", "Synthetix OS workflow completed.")
                httpx.post(webhook_url, json={"text": text}, timeout=10.0)
                print(f"[Slack] Message sent")
                return {"slack_sent": True}
            except Exception as e:
                print(f"[Slack] Failed: {e}")

        print("[STUB] Sending Slack message...")
        return {"slack_sent": True, "stub": True}


class TelegramMessageAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        from integrations.telegram import send_message

        chat_id = (
            config.get("chat_id")
            or os.environ.get("TELEGRAM_CHAT_ID")
        )
        message = config.get("message", "Synthetix OS notification")

        if chat_id:
            try:
                send_message(str(chat_id), message)
                print(f"[Telegram] Message sent to {chat_id}")
                return {"telegram_sent": True}
            except Exception as e:
                print(f"[Telegram] Failed: {e}")

        print(f"[STUB] Telegram message: {message}")
        return {"telegram_sent": True, "stub": True}