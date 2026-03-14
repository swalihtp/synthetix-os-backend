from .ai_actions import (
    AnalyzeEmailAction,
    ClassifyIntentAction,
    GenerateReplyAction,
    ExtractContentAction,
    AdaptForPlatformAction,
    DetectMeetingIntentAction,
)
from .base import BaseAction
from .gmail_actions import (
    GmailFetchEmailAction,
    GmailSendReplyAction,
)
from .calendar_actions import (
    CalendarCheckAvailabilityAction,
    CalendarCreateEventAction,
)
from .system_actions import (
    SchedulePostsAction,
    NotifyUserAction,
    SlackMessageAction,
    TelegramMessageAction,
)

ACTION_REGISTRY = {
    # AI actions
    "ai.analyze_email":         AnalyzeEmailAction,
    "ai.classify_intent":       ClassifyIntentAction,
    "ai.generate_reply":        GenerateReplyAction,
    "ai.extract_content":       ExtractContentAction,
    "ai.adapt_twitter":         AdaptForPlatformAction,
    "ai.adapt_linkedin":        AdaptForPlatformAction,
    "ai.adapt_instagram":       AdaptForPlatformAction,
    "ai.detect_meeting_intent": DetectMeetingIntentAction,

    # Gmail actions
    "gmail.fetch_email":        GmailFetchEmailAction,
    "gmail.send_reply":         GmailSendReplyAction,

    # Calendar actions
    "calendar.check_availability": CalendarCheckAvailabilityAction,
    "calendar.create_event":       CalendarCreateEventAction,

    # System actions
    "system.schedule_posts":    SchedulePostsAction,
    "system.notify_user":       NotifyUserAction,
    "slack.send_message":       SlackMessageAction,
    "telegram.send_message":    TelegramMessageAction,
}


def get_action(action_name: str) -> BaseAction:
    """Get an action instance by name. Raises if not found."""
    action_class = ACTION_REGISTRY.get(action_name)
    if not action_class:
        raise Exception(
            f"Unknown action: '{action_name}'. "
            f"Available: {list(ACTION_REGISTRY.keys())}"
        )
    return action_class()