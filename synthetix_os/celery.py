import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE','synthetix.settings')

# app=Celery('synthetix_os')
app = Celery('tasks', broker='redis://localhost:6379/0')
app.config_from_object('django.conf:settings',namespace='CELERY')