from langgraph.graph import StateGraph, END
from .state import MarketIntelligenceState
from .node.research_gap_detection import research_gap_detection_node
from .routers.route_gap_research import route_gap_research
from .node.load_documents import load_documents_node
from .node.crawl_company_website import crawl_company_website_node
from .node.company_profiling import company_profiling_node
from .node.competitor_discovery import competitor_discovery_node
from .node.competitor_research import competitor_research_node
from .node.market_trend_analysis import market_trend_analysis_node
from .node.swot_generation import swot_generation_node
from .node.recommendation_generation import recommendation_generation_node
from .node.executive_summary_generation import executive_summary_generation_node
from .node.report_generation import report_generation_node
from .node.additional_research import additional_research_node


workflow = StateGraph(MarketIntelligenceState)

workflow.add_node("load_documents", load_documents_node)
workflow.add_node("crawl_company_website", crawl_company_website_node)
workflow.add_node("company_profiling", company_profiling_node)
workflow.add_node("research_gap_detection", research_gap_detection_node)
workflow.add_node("competitor_discovery", competitor_discovery_node)
workflow.add_node("competitor_research", competitor_research_node)
workflow.add_node("market_trend_analysis", market_trend_analysis_node)
workflow.add_node("swot_generation", swot_generation_node)
workflow.add_node("recommendation_generation", recommendation_generation_node)
workflow.add_node("executive_summary_generation", executive_summary_generation_node)
workflow.add_node("report_generation", report_generation_node)
workflow.add_node("additional_research", additional_research_node)



workflow.set_entry_point("load_documents")
workflow.add_edge("load_documents", "crawl_company_website")
workflow.add_edge("crawl_company_website", "company_profiling")
workflow.add_edge("company_profiling","research_gap_detection" )



workflow.add_conditional_edges(
    "research_gap_detection",
    route_gap_research,
    {
        "additional_research": "additional_research",
        "competitor_discovery": "competitor_discovery",
    },
)

workflow.add_edge("additional_research", "competitor_discovery")

workflow.add_edge("competitor_discovery", "competitor_research")

workflow.add_edge("competitor_research", "market_trend_analysis")

workflow.add_edge("market_trend_analysis", "swot_generation")

workflow.add_edge("swot_generation", "recommendation_generation")

workflow.add_edge("recommendation_generation", "executive_summary_generation")

workflow.add_edge("executive_summary_generation", "report_generation")

workflow.add_edge("report_generation", END)

market_intelligence_app = workflow.compile()
