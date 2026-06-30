from workflows.market_inteligence_workflow.services.ai_service import analyze_competitor

from workflows.market_inteligence_workflow.services.tavily_service import research_competitor


def competitor_research_node(state):

    profiles = []

    competitors = state.get("discovered_competitors", [])

    for competitor in competitors:

        research = research_competitor(competitor)

        profile = analyze_competitor(research)

        profiles.append(profile)

    return {"competitor_profiles": profiles}
