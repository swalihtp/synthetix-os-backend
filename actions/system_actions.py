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
        message = config.get("message", "Your workflow completed successfully.")
        print(f"[STUB] Notifying user via {channel}: {message}")
        return {"notification_sent": True, "channel": channel}


class SlackMessageAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        print(f"[STUB] Sending Slack message...")
        return {"slack_sent": True}


class TelegramMessageAction(BaseAction):
    def execute(self, config: dict, context: dict) -> dict:
        print(f"[STUB] Sending Telegram message...")
        return {"telegram_sent": True}