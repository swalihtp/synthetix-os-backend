from workflows.models import Workflow, WorkflowRun
from .models import Event


def dispatch_event(event: Event):
    """
    Find all active workflows matching this event type
    for this user, and trigger a WorkflowRun for each.
    """
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
            context={"payload": event.payload},
        )
        # Import here to avoid circular imports
        from workflows.tasks import execute_workflow
        execute_workflow.delay(str(run.id))

    event.status = 'done'
    event.save()