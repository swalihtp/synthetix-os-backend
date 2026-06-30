from workflows.email_workflow.state import EmailWorkflowState
from workflows.models import WorkflowExecution, EmailExecutionResult
from django.utils import timezone
from agent.models import Agent

def should_continue(state:EmailWorkflowState)->str:
    if state.get('skip_workflow', False):
        
        exeution = WorkflowExecution.objects.get(id=state.get("execution_id"))
        exeution.status = "SUCCESS"
        exeution.ended_at = timezone.now()
        exeution.save(update_fields=["status","ended_at"])
        
        agent = Agent.objects.get(id=state["agent_id"])
        
        EmailExecutionResult.objects.create(
            agent = agent,
            workflow_execution = exeution,
            email_id = state.get("email_id"),
            result = "SKIPPED"
        )
        
        return 'end'
    return "continue"