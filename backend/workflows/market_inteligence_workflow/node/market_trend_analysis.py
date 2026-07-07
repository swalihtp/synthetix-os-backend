from workflows.market_inteligence_workflow.services.tavily_service import research_market_trends

from workflows.market_inteligence_workflow.services.ai_service import analyze_market_trends


def market_trend_analysis_node(state):

    profile = state["company_profile"]

    trend_data = research_market_trends(profile)

    trends = analyze_market_trends(trend_data)

    return {"market_trends": trends}
