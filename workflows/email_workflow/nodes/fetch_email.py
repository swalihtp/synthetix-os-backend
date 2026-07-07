from workflows.email_workflow.state import EmailWorkflowState
from integrations.gmail import get_email_details, get_gmail_service
from integrations.models import ProcessedEmail
from accounts.models import User
from workflows.utils.realtime import send_workflow_update
from django.db import IntegrityError


def fetch_email_node(state: EmailWorkflowState) -> EmailWorkflowState:
    send_workflow_update(
        state["agent_id"],
        {
            "log": "Fetching Email",
            "progress": 25,
            "step": {"index": 2, "name": "Fetching", "status": "runnig"},
        },
    )

    user = User.objects.get(id=state["user_id"])
    service = get_gmail_service(user)
    raw_email = get_email_details(service, state["email_id"])
    
    print(f"RAW EMAIL:{raw_email}")

    if raw_email:
        state["raw_email"] = raw_email

        try:
            obj, created = ProcessedEmail.objects.get_or_create(
                message_id=state["email_id"],
                defaults={"user": user},
            )

            if not created:
                return {"skip_workflow": True}

        except IntegrityError:
            return {"skip_workflow": True}

        send_workflow_update(
            state["agent_id"],
            {
                "log": "Fetched Email Successfully",
                "progress": 30,
                "step": {"index": 3, "name": "Fetching", "status": "done"},
            },
        )
        return state
    state["skip_workflow"] = True
    return state
