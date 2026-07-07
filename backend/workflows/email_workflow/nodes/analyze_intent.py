from workflows.email_workflow.services.ai.ai_service import analyze_intent
from workflows.models import AIUsageLog, WorkflowExecution

def analyze_intention_node(state):
    
    temp = list(state["ai_reply_categories"])
    temp.extend(state["human_review_categories"])
    temp.extend(state["ignore_categories"])

    print("SUBJECT LENGTH:", len(state["raw_email"].get("subject", "")))
    print("BODY LENGTH:", len(state["raw_email"].get("body", "")))

    print(state["raw_email"].get("body", "")[:1000])

    res = analyze_intent(
        subject=state["raw_email"].get("subject", ""),
        body=state["raw_email"].get("body", ""),
        intentions=temp,
    )
    
    execution = WorkflowExecution.objects.get(id=state.get("execution_id"))

    AIUsageLog.objects.create(
        workflow_execution=execution,
        provider="OPENROUTER",
        model_name="nvidia/nemotron-3-super-120b-a12b:free",
        operation="INTENT_ANALYSIS",
    )
    
    return {"intention": res, "reason_for_review":res.get("reason","")}


