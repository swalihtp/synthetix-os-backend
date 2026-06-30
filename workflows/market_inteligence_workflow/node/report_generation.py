from workflows.market_inteligence_workflow.services.ai_service import generate_market_report


def report_generation_node(state):

    report = generate_market_report(
        company_profile=state["company_profile"],
        competitors=state["competitor_profiles"],
        trends=state["market_trends"],
        swot=state["swot"],
        recommendations=state["recommendations"],
        executive_summary=state["executive_summary"],
    )

    return {"report_markdown": report}
