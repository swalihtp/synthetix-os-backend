from workflows.email_workflow.state import EmailWorkflowState
from workflows.models import WorkflowExecution,EmailExecution
from django.utils import timezone
from agent.models import Agent


def decide_process_after_intent_analysis_node(state: EmailWorkflowState):
    intention = state["intention"]
    intent = intention.get("intention", "")
    confidence = intention.get("confidence", 0)
    print(f"AI RESPOND CATEGORY:{state.get("ai_reply_categories")}")
    print(f"HUMAN_REVIEW_CATEGORIES CATEGORY:{state.get("human_review_categories")}")
    print(f"IGNORE_CATEGORIES CATEGORY:{state.get("ignore_categories")}")
    if intent in state["ignore_categories"]:
        print(F"REQUEST IS SKIPPED BECAUSE THE INTENTION IS INCLUDE IN IGNORE CATEGORY {intent}")
        result = "skip"
        exeution = WorkflowExecution.objects.get(id=state.get("execution_id"))
        exeution.status = "SUCCESS"
        exeution.ended_at = timezone.now()
        exeution.save(update_fields=["status", "ended_at"])
        
        agent = Agent.objects.get(user__id=state.get("user_id"), name__iexact="Smart Email Agent")
        
        email_execution = EmailExecution.objects.get(id=state.get("email_execution_id"))

        email_execution.agent = agent
        email_execution.email_id = state.get("email_id")
        email_execution.thread_id = state.get("raw_email", {}).get("thread_id")
        email_execution.sender = state.get("raw_email").get("from")
        email_execution.recipient = agent.user.email
        email_execution.original_subject = state.get("raw_email", {}).get("subject", "")
        email_execution.original_body = state.get("raw_email").get("body", "")
        email_execution.detected_intent = state.get("intention", {}).get("intention")
        email_execution.confidence_score = state.get("intention", {}).get("confidence")
        email_execution.reply_subject = state.get("reply_subject", "")
        email_execution.reply_body = state.get("reply_body", "")
        email_execution.result = "SKIPPED"
        email_execution.review_reason = state.get("reason_for_review", "")
        email_execution.processed_at = timezone.now()

        email_execution.save()        
            
        return result

    if intent in state["ai_reply_categories"]:
        if confidence >= 0.85:
            result = "process"
            
            return result
        state["reason_for_review"] = intention.get("reason")
        result = "review"
        print(f"REQUEST IS STEPPED ASIDED FOR HUMAN REVIEW INTENTION:{intent} CONFIDENCE:{confidence} because the confidence is low")
        
        return result

    if intent in state["human_review_categories"]:
        print(f"REQUEST IS STEPPED ASIDED FOR HUMAN REVIEW INTENTION:{intent} because intent is included in human_review_categories")
        result = "review"
         
        return result

    result = "review"
    
    exeution = WorkflowExecution.objects.get(id=state.get("execution_id"))
    exeution.status = "SUCCESS"
    exeution.ended_at = timezone.now()
    exeution.save(update_fields=["status", "ended_at"])
    
    print("LAST FALLBACK REVIEW")
    return result
