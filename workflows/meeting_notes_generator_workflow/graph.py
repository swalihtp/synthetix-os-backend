from langgraph.graph import StateGraph, START, END

from workflows.meeting_notes_generator_workflow.nodes.initialize_node import (
    initialize_node,
)
from workflows.meeting_notes_generator_workflow.nodes.extract_text_node import (
    extract_text_node,
)
from workflows.meeting_notes_generator_workflow.nodes.generate_meeting_summary_node import (
    generate_meeting_summary_node,
)
from workflows.meeting_notes_generator_workflow.nodes.store_summary_node import (
    store_summary_node,
)
from workflows.meeting_notes_generator_workflow.routers.can_extract_router import (
    can_extract_router,
)
from workflows.meeting_notes_generator_workflow.state import MeetingWorkflowState


graph = StateGraph(MeetingWorkflowState)

# Register nodes
graph.add_node("initialize_node", initialize_node)
graph.add_node("extract_text_node", extract_text_node)
graph.add_node("generate_meeting_summary_node", generate_meeting_summary_node)
graph.add_node("store_summary_node", store_summary_node)

# Edges
graph.add_edge(START, "initialize_node")
graph.add_edge("initialize_node", "extract_text_node")

graph.add_conditional_edges(
    "extract_text_node",
    can_extract_router,
    {"continue": "generate_meeting_summary_node", "end": END},
)

graph.add_edge("generate_meeting_summary_node", "store_summary_node")
graph.add_edge("store_summary_node", END)

meeting_notes_app = graph.compile()
