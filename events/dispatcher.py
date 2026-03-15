from workflows.models import Workflow, WorkflowRun
from .models import Event


def dispatch_event(event: Event):
    matching_workflows = Workflow.objects.filter(
        trigger_type=event.event_type,
        agent__user=event.user,
        is_active=True
    )

    if not matching_workflows.exists():
        event.status = 'done'
        event.save()
        return

    event.status = 'processing'
    event.save()

    for workflow in matching_workflows:
        run = WorkflowRun.objects.create(
            workflow=workflow,
            event=event,
            status='pending',
            context={
                "payload": event.payload,
                "user_id": str(event.user.id),  # ← add this
            },
        )
        from workflows.tasks import execute_workflow
        execute_workflow.delay(str(run.id))

    event.status = 'done'
    event.save()