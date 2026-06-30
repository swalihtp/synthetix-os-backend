import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.environ.get("DJANGO_SETTINGS_MODULE", "synthetix_os.settings.dev"),
)

app = Celery('synthetix_os')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "renew-gmail-watches-daily": {
        "task": "workflows.tasks.renew_gmail_watches",
        "schedule": crontab(hour=0, minute=0),
    },
    "run-market-intelligence-daily": {
        "task": "workflows.tasks.run_market_intelligence",
        "schedule": crontab(hour=6, minute=0),
    },
}
