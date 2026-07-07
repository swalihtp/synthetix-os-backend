from workflows.gmail_notification.state import GmailNotificationState
from django.core.cache import cache

def deduplicate_pubsub_node(state):

    message_id = state.get("pubsub_msg_id")

    if message_id:
        cache_key = f"pubsub_msg_{message_id}"

        if cache.get(cache_key):
            state["skip_workflow"] = True
            return state

        cache.set(cache_key, True, timeout=300)

    return state
