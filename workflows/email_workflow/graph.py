from langgraph.graph import StateGraph, START, END
from workflows.email_workflow.state import EmailWorkflowState
from workflows.email_workflow.nodes.deduplicate import deduplicate_node
from workflows.email_workflow.nodes.fetch_email import fetch_email_node
from workflows.email_workflow.nodes.extract_attachments import extract_attachments_node
from workflows.email_workflow.nodes.document_processing import document_processing_node
from workflows.email_workflow.nodes.ai import ai_node
from workflows.email_workflow.nodes.reply import reply_node
from workflows.email_workflow.routers.should_continue import should_continue
from workflows.email_workflow.routers.decide_process_router import decide_process_router
from workflows.email_workflow.routers.decision_router import decision_router
from workflows.email_workflow.nodes.human_review import create_human_review_node
from workflows.email_workflow.routers.decide_to_human_review import (
    decision_router_for_human_review,
)
from workflows.email_workflow.nodes.initialize import initial_node
from workflows.email_workflow.nodes.analyze_intent import analyze_intention_node
from workflows.email_workflow.routers.decide_process_after_intent_analysis import (
    decide_process_after_intent_analysis_node,
)
from workflows.email_workflow.nodes.create_email_execution import (
    create_email_execution_node,
)

graph = StateGraph(EmailWorkflowState)

graph.add_node("initial_node", initial_node)
graph.add_node("deduplicate_node", deduplicate_node)
graph.add_node("fetch_email_node", fetch_email_node)
graph.add_node("create_email_execution_node", create_email_execution_node)
graph.add_node("analyze_intention_node", analyze_intention_node)
graph.add_node("extract_attachments_node", extract_attachments_node)
graph.add_node("document_processing_node", document_processing_node)
graph.add_node("ai_node", ai_node)
graph.add_node("create_human_review_node", create_human_review_node)
graph.add_node("reply_node", reply_node)

graph.add_edge(START, "initial_node")
graph.add_edge("initial_node", "deduplicate_node")

graph.add_conditional_edges(
    "deduplicate_node", should_continue, {"continue": "fetch_email_node", "end": END}
)
graph.add_edge("fetch_email_node", "create_email_execution_node")

graph.add_conditional_edges(
    "create_email_execution_node",
    should_continue,
    {"continue": "extract_attachments_node", "end": END},
)


graph.add_conditional_edges(
    "extract_attachments_node",
    decide_process_router,
    {"process": "document_processing_node", "skip": "analyze_intention_node"},
)
graph.add_conditional_edges(
    "document_processing_node",
    decision_router_for_human_review,
    {
        "human_review": "create_human_review_node",
        "analyze_intent": "analyze_intention_node",
    },
)

graph.add_conditional_edges(
    "analyze_intention_node",
    decide_process_after_intent_analysis_node,
    {"skip": END, "review": "create_human_review_node", "process": "ai_node"},
)


graph.add_conditional_edges(
    "ai_node",
    decision_router,
    {"human_review": "create_human_review_node", "send_reply": "reply_node"},
)

graph.add_edge("create_human_review_node", END)
graph.add_edge("reply_node", END)

email_workflow_app = graph.compile()

