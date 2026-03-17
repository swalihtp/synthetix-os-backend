from celery import shared_task
from django.utils import timezone
from integrations.models import Integration
from integrations.gmail_watch import register_gmail_watch
from django.contrib.auth import get_user_model
from celery.schedules import crontab

User=get_user_model()


@shared_task(bind=True, max_retries=3)
def execute_workflow(self, run_id: str):
    from .models import WorkflowRun
    from actions.registry import get_action

    try:
        run = WorkflowRun.objects.get(id=run_id)
    except WorkflowRun.DoesNotExist:
        return

    run.status = 'running'
    run.save()

    steps = run.workflow.steps.all()

    try:
        for step in steps:
            action = get_action(step.action)

            # For platform-specific AI actions, inject platform into config
            config = step.config.copy()
            if step.action.startswith("ai.adapt_"):
                platform = step.action.replace("ai.adapt_", "")
                config["platform"] = platform

            result = action.execute(config, run.context)
            run.context.update(result)
            run.current_step = step.order
            run.save()

        run.status = 'completed'

    except Exception as e:
        run.status = 'failed'
        run.error = str(e)

        # Retry if step says so
        if run.workflow.steps.filter(
            order=run.current_step,
            on_failure='retry'
        ).exists():
            raise self.retry(exc=e, countdown=60)

    finally:
        run.finished_at = timezone.now()
        run.save()
        

@shared_task
def renew_gmail_watches():
    """Renew Gmail watch for all users with Gmail integration."""


    
    integrations = Integration.objects.filter(
        provider='gmail',
        is_active=True
    )

    for integration in integrations:
        try:
            register_gmail_watch(integration.user)
            print(f"[Gmail Watch] Renewed for {integration.user.email}")
        except Exception as e:
            print(f"[Gmail Watch] Failed for {integration.user.email}: {e}")