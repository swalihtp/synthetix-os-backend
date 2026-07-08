def route_gap_research(state):

    gaps = state.get("research_gaps", [])

    if gaps:
        return "additional_research"

    return "competitor_discovery"
