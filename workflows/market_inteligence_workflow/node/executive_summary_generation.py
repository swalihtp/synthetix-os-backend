from workflows.market_inteligence_workflow.services.ai_service import generate_executive_summary


def executive_summary_generation_node(state):

    summary = generate_executive_summary(
        company_profile=state["company_profile"],
        competitors=state["competitor_profiles"],
        trends=state["market_trends"],
        swot=state["swot"],
    )

    return {"executive_summary": summary}
