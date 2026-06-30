from workflows.market_inteligence_workflow.state import MarketState

def decide_process_router(state:MarketState):
    if state.get('skip_workflow'):
        return 'end'
    if state.get('company_website'):
        return 'process'
    return "skip"