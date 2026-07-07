from workflows.gmail_notification.state import GmailNotificationState

def validate_payload_node(state:GmailNotificationState)->GmailNotificationState:
    payload = state["payload"]

    state["email_address"] = payload.get("emailAddress")
    state["history_id"] = payload.get("historyId")
    state["pubsub_msg_id"] = payload.get("pubsub_msg_id")

    if not state["email_address"]:
        state["skip_workflow"] = True

    return state