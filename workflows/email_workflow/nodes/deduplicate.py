from workflows.email_workflow.state import EmailWorkflowState
from integrations.models import ProcessedEmail
from workflows.utils.realtime import send_workflow_update
from agent.models import Agent
from accounts.models import User

def deduplicate_node(state: EmailWorkflowState) -> EmailWorkflowState:
    user = User.objects.get(id=state['user_id'])

    send_workflow_update(
        str(state["agent_id"]),
        {
            "log": "Checking duplicate email...",
            "progress": 10,
            "step": {"index": 0, "name": "Deduplicate", "status": "running"},
        },
    )
    processed = ProcessedEmail.objects.filter(message_id=state["email_id"], user=user).exists()
    if processed:
        state["skip_workflow"] = True
        return state
    else:
        send_workflow_update(
            str(state["agent_id"]),
            {
                "log": "Email is unique not duplicate",
                "progress": 15,
                "step": {"index": 1, "name": "Deduplicate", "status": "done"},
            },
        )
        return state
