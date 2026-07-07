from workflows.market_inteligence_workflow.services.ai_service import generate_swot


def swot_generation_node(state):

    swot = generate_swot(
        company_profile=state["company_profile"],
        competitors=state["competitor_profiles"],
        trends=state["market_trends"],
    )

    return {"swot": swot}
