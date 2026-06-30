from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

def sync_workflow_schedule(workflow):
    if workflow.trigger_type != "schedule":
        return

    cron = workflow.trigger_config.get("cron")
    if not cron:
        return

    minute, hour, day, month, dow = cron.split()

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=minute,
        hour=hour,
        day_of_month=day,
        month_of_year=month,
        day_of_week=dow,
    )

    PeriodicTask.objects.update_or_create(
        name=f"workflow-{workflow.id}",
        defaults={
            "crontab": schedule,
            "task": "workflows.tasks.trigger_workflow",
            "args": json.dumps([str(workflow.id)]),
        }
    )