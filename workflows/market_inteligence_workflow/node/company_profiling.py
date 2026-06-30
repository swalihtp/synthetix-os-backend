from workflows.market_inteligence_workflow.services.ai_service import build_company_profile


def company_profiling_node(state):

    profile = build_company_profile(
        company_name=state["company_name"],
        company_description=state["company_description"],
        documents=state.get("document_contents", []),
        website_content=state.get("website_content", {}),
    )

    return {"company_profile": profile}
