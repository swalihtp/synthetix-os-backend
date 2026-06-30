from workflows.market_inteligence_workflow.services.tavily_service import discover_competitors


def competitor_discovery_node(state):

    profile = state["company_profile"]

    competitors = discover_competitors(profile)

    return {"discovered_competitors": competitors}
