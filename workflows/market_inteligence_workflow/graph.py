# workflows/market_inteligence_workflow/graph.py

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from workflows.market_inteligence_workflow.state import (
    MarketState,
)

# =========================================================
# NODES
# =========================================================

from workflows.market_inteligence_workflow.node.load_agent_configuration_node import (
    load_agent_configuration_node,
)

from workflows.market_inteligence_workflow.node.fetch_company_website import (
    fetch_company_node,
)

from workflows.market_inteligence_workflow.node.fetch_competitors_websites import (
    fetch_competitors_websites_node,
)

from workflows.market_inteligence_workflow.node.market_research import (
    market_research_node,
)

from workflows.market_inteligence_workflow.node.competitor_analysis import (
    competitor_analysis_node,
)

from workflows.market_inteligence_workflow.node.trend_analysis import (
    trend_analysis_node,
)

from workflows.market_inteligence_workflow.node.sentiment_analysis import (
    sentiment_analysis_node,
)

from workflows.market_inteligence_workflow.node.swot_analysis import (
    swot_analysis_node,
)

from workflows.market_inteligence_workflow.node.report_generator import (
    report_generator_node,
)

from workflows.market_inteligence_workflow.node.pdf_generator import (
    pdf_generator_node,
)

from workflows.market_inteligence_workflow.node.upload_to_s3 import (
    upload_to_s3_node,
)

from workflows.market_inteligence_workflow.node.send_report import (
    send_report_node,
)

# =========================================================
# ROUTERS
# =========================================================

from workflows.market_inteligence_workflow.routers.decide_process_router import (
    decide_process_router,
)

# =========================================================
# GRAPH
# =========================================================

graph = StateGraph(MarketState)

# =========================================================
# REGISTER NODES
# =========================================================

graph.add_node(
    "load_config",
    load_agent_configuration_node,
)

graph.add_node(
    "fetch_company_node",
    fetch_company_node,
)

graph.add_node(
    "market_research_node",
    market_research_node,
)

graph.add_node(
    "competitor_analysis_node",
    competitor_analysis_node,
)

graph.add_node(
    "trend_analysis_node",
    trend_analysis_node,
)

graph.add_node(
    "sentiment_analysis_node",
    sentiment_analysis_node,
)

graph.add_node(
    "fetch_competitors_websites_node",
    fetch_competitors_websites_node,
)

graph.add_node(
    "swot_analysis_node",
    swot_analysis_node,
)

graph.add_node(
    "report_generator_node",
    report_generator_node,
)

graph.add_node(
    "pdf_generator_node",
    pdf_generator_node,
)

graph.add_node(
    "upload_to_s3_node",
    upload_to_s3_node,
)

graph.add_node(
    "send_report_node",
    send_report_node,
)

# =========================================================
# START
# =========================================================

graph.add_edge(
    START,
    "load_config",
)

# =========================================================
# CONDITIONAL ROUTING
# =========================================================

graph.add_conditional_edges(
    "load_config",
    decide_process_router,
    {
        "process": "fetch_company_node",
        "skip": "market_research_node",
        "end": END,
    },
)

# =========================================================
# COMPANY WEBSITE FETCH
# =========================================================

graph.add_edge(
    "fetch_company_node",
    "market_research_node",
)

# =========================================================
# PARALLEL ANALYSIS
# =========================================================

graph.add_edge(
    "market_research_node",
    "fetch_competitors_websites_node",
)

graph.add_edge(
    "fetch_competitors_websites_node",
    "competitor_analysis_node",
)

graph.add_edge(
    "fetch_competitors_websites_node",
    "trend_analysis_node",
)

graph.add_edge(
    "fetch_competitors_websites_node",
    "sentiment_analysis_node",
)

# =========================================================
# MERGE POINT
# =========================================================

graph.add_edge(
    "competitor_analysis_node",
    "swot_analysis_node",
)

graph.add_edge(
    "trend_analysis_node",
    "swot_analysis_node",
)

graph.add_edge(
    "sentiment_analysis_node",
    "swot_analysis_node",
)

# =========================================================
# REPORT GENERATION
# =========================================================

graph.add_edge(
    "swot_analysis_node",
    "report_generator_node",
)

# =========================================================
# PDF GENERATION
# =========================================================

graph.add_edge(
    "report_generator_node",
    "pdf_generator_node",
)

# =========================================================
# S3 UPLOAD
# =========================================================

graph.add_edge(
    "pdf_generator_node",
    "upload_to_s3_node",
)

# =========================================================
# EMAIL DELIVERY
# =========================================================

graph.add_edge(
    "upload_to_s3_node",
    "send_report_node",
)

# =========================================================
# END
# =========================================================

graph.add_edge(
    "send_report_node",
    END,
)

# =========================================================
# COMPILE
# =========================================================

market_intelligence_app = graph.compile()
