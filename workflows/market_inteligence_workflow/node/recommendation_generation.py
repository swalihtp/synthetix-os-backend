from workflows.market_inteligence_workflow.services.ai_service import generate_recommendations


def recommendation_generation_node(state):

    recommendations = generate_recommendations(
        company_profile=state["company_profile"],
        swot=state["swot"],
        competitors=state["competitor_profiles"],
        trends=state["market_trends"],
    )

    return {"recommendations": recommendations}
