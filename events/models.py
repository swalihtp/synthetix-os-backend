from django.db import models
from workflows.models import Workflow
from django.contrib.auth import get_user_model

User=get_user_model()

class Event(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        DONE = 'done', 'Done'
        FAILED = 'failed', 'Failed'

    event_type = models.CharField(max_length=100)   # "gmail.email_received"
    payload = models.JSONField()                     # raw webhook data
    source = models.CharField(max_length=100)        # "gmail", "webhook", "schedule"
    status = models.CharField(max_length=20, choices=Status.choices, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkflowRun(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        PAUSED = 'paused', 'Paused'

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default='pending')
    context = models.JSONField(default=dict)   # shared state passed between steps
    current_step = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
