from workflows.market_inteligence_workflow.services.tavily_service import (
    perform_gap_research,
)
from workflows.market_inteligence_workflow.services.ai_client import ai_client


def additional_research_node(state):

    gaps = state.get("research_gaps", [])

    if not gaps:

        return {}

    research = perform_gap_research(
        company_name=state["company_name"],
        company_profile=state["company_profile"],
        gaps=gaps,
    )

    enriched_profile = ai_client.execute(
        task="profile_enrichment",
        payload={
            "company_profile": state["company_profile"],
            "research_gaps": gaps,
            "additional_research": research,
        },
    )

    return {
        "company_profile": enriched_profile["data"],
        "additional_research": research,
    }
