import uuid
from django.db import models
from agent.models import Agent

class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=200)
    trigger_type = models.CharField(max_length=100)
    trigger_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.trigger_type}"

class WorkflowStep(models.Model):
    STEP_TYPES = [
        ('ai', 'AI Action'),
        ('system', 'System Action'),
        ('condition', 'Condition'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    action = models.CharField(max_length=100)
    config = models.JSONField(default=dict)
    order = models.PositiveIntegerField()
    on_failure = models.CharField(max_length=20, default='stop')

    def __str__(self):
        return f"Step {self.order}: {self.action}"

    class Meta:
        ordering = ['order']

class WorkflowRun(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='runs')
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    context = models.JSONField(default=dict)
    current_step = models.PositiveIntegerField(default=0)
    error = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Run {self.id} - {self.status}"