from workflows.email_workflow.state import EmailWorkflowState
from workflows.email_workflow.services.ai.ai_service import ai_service
from accounts.models import User
from workflows.utils.realtime import send_workflow_update
from workflows.models import AIUsageLog, WorkflowExecution


def ai_node(state: EmailWorkflowState)-> EmailWorkflowState:

    send_workflow_update(
        state["agent_id"],
        {
            "log": "AI reasonings ongoing",
            "progress": 75,
            "step": {"index": 8, "name": "AI reasoning", "status": "runnig"},
        },
    )
    user = User.objects.filter(id=state["user_id"]).first()

    if not user:
        state["skip_workflow"] = True
        return state
    
    user_context = {
        'name':user.full_name,
        'email': user.email
    }
    temp = state.get("raw_email", {}).copy()
    temp.pop("attachments", None)
    res = ai_service(temp,state.get('extracted_documents', []),str(state["user_id"]),state.get("email_id",""),user_context)

    print("AI_RESPONSE",res)
    
    if not res:
        state["skip_workflow"] = True
        return state

    state["requires_human"] = res["requires_human"]
    state["confidence"] = res["confidence"]
    state["reply_subject"] = res["reply_subject"]
    state["reply_body"] = res["reply_body"]
    
    send_workflow_update(
        state["agent_id"],
        {
            "log": "AI reasonings successfully completed",
            "progress": 85,
            "step": {"index": 9, "name": "AI reasoning", "status": "done"},
        },
    )
    
    execution = WorkflowExecution.objects.get(id=state.get("execution_id"))
    
    AIUsageLog.objects.create(
        workflow_execution=execution,
        provider="OPENROUTER",
        model_name="nvidia/nemotron-3-super-120b-a12b:free",
        operation="REPLY_GENERATION",
    )    
    

    return state
