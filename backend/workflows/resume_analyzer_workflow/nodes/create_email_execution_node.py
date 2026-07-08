from workflows.resume_analyzer_workflow.state import ResumeWorkflowState
from workflows.models import ResumeExecution, WorkflowExecution

def create_resume_execution_node(state:ResumeWorkflowState):
    workflow_execution = WorkflowExecution.objects.get(id=state.get("execution_id"))
    resume_execution = ResumeExecution.objects.create(workflow_execution=workflow_execution)
    
    return {"resume_execution_id":str(resume_execution.id)}