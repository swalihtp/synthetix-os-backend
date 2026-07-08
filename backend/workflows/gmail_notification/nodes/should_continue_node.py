from workflows.gmail_notification.state import GmailNotificationState


def should_continue(state:GmailNotificationState)->GmailNotificationState:
    if state.get("skip_workflow"):
        return "end"

    return "continue"