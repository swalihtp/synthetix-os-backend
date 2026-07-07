from langgraph.graph import StateGraph, START, END
from workflows.gmail_notification.nodes.validate_payload_node import validate_payload_node
from workflows.gmail_notification.nodes.resolve_user_node import resolve_user_node
from workflows.gmail_notification.nodes.fetch_history_changes_node import fetch_history_changes_node
from workflows.gmail_notification.nodes.deduplicate_pubsub_node import deduplicate_pubsub_node
from workflows.gmail_notification.nodes.enqueue_email_jobs_node import enqueue_email_jobs_node
from workflows.gmail_notification.nodes.should_continue_node import should_continue
from workflows.gmail_notification.state import GmailNotificationState


graph = StateGraph(GmailNotificationState)

graph.add_node('validate_payload',validate_payload_node)
graph.add_node('deduplicate_pubsub_node',deduplicate_pubsub_node)
graph.add_node('resolve_user_node',resolve_user_node)
graph.add_node('fetch_history_changes_node',fetch_history_changes_node)
graph.add_node('enqueue_email_jobs_node',enqueue_email_jobs_node)

graph.add_edge(START,'validate_payload')
graph.add_conditional_edges(
    "validate_payload",
    should_continue,
    {
        "continue": "deduplicate_pubsub_node",
        "end": END,
    }
)

graph.add_conditional_edges(
    "deduplicate_pubsub_node",
    should_continue,
    {
        "continue": "resolve_user_node",
        "end": END,
    }
)

graph.add_conditional_edges(
    "resolve_user_node",
    should_continue,
    {
        "continue": "fetch_history_changes_node",
        "end": END,
    }
)


graph.add_edge('fetch_history_changes_node','enqueue_email_jobs_node')
graph.add_edge('enqueue_email_jobs_node',END)

gmail_notification_app = graph.compile()


