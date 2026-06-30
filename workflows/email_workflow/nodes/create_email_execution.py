from workflows.models import WorkflowExecution, EmailExecution
from agent.models import Agent


def create_email_execution_node(state):

    execution = WorkflowExecution.objects.get(id=state["execution_id"])

    agent = Agent.objects.get(id=state["agent_id"])

    email_execution = EmailExecution.objects.create(
        agent=agent,
        workflow_execution=execution,
    )

    state["email_execution_id"] = str(email_execution.id)

    return state
