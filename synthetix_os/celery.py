import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'synthetix_os.settings.dev')

app = Celery('synthetix_os')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()