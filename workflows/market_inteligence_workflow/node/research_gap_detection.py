from workflows.market_inteligence_workflow.services.ai_service import detect_research_gaps


def research_gap_detection_node(state):

    gaps = detect_research_gaps(state["company_profile"])

    return {"research_gaps": gaps}
