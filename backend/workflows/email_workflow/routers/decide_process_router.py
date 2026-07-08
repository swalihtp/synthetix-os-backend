from workflows.email_workflow.state import EmailWorkflowState

def decide_process_router(state:EmailWorkflowState)->str:
    if state.get("attachments"):
        return 'process'
        
    return "skip"

