from workflows.market_inteligence_workflow.state import MarketState

def decide_process_router2(state:MarketState):
    if state.get('competitor_websites'):
        return 'process'
    return "skip"