from langgraph.graph import StateGraph, START, END

from workflows.resume_analyzer_workflow.nodes.initialize_node import initialize_node
from workflows.resume_analyzer_workflow.nodes.extract_text_node import extract_text_node
from workflows.resume_analyzer_workflow.nodes.resume_analysis_node import (
    resume_analysis_node,
)
from workflows.resume_analyzer_workflow.nodes.store_analysis_node import (
    store_analysis_node,
)
from workflows.resume_analyzer_workflow.routers.can_extract_router import (
    can_extract_router,
)
from workflows.resume_analyzer_workflow.state import ResumeWorkflowState


graph = StateGraph(ResumeWorkflowState)

# Register nodes
graph.add_node("initialize_node", initialize_node)
graph.add_node("extract_text_node", extract_text_node)
graph.add_node("resume_analysis_node", resume_analysis_node)
graph.add_node("store_analysis_node", store_analysis_node)

# Edges
graph.add_edge(START, "initialize_node")
graph.add_edge("initialize_node", "extract_text_node")

graph.add_conditional_edges(
    "extract_text_node",
    can_extract_router,
    {"continue": "resume_analysis_node", "end": END},
)

# Single analysis node -> persist -> done
graph.add_edge("resume_analysis_node", "store_analysis_node")
graph.add_edge("store_analysis_node", END)

resume_analyzer_app = graph.compile()
