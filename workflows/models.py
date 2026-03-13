from django.db import models
from agent.models import Agent

class Workflow(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    trigger_type = models.CharField(max_length=100)  # e.g. "gmail.email_received"
    trigger_config = models.JSONField(default=dict)   # filters, conditions
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WorkflowStep(models.Model):
    class StepType(models.TextChoices):
        AI_ACTION = 'ai', 'AI Action'
        SYSTEM_ACTION = 'system', 'System Action'
        CONDITION = 'condition', 'Condition'

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=20, choices=StepType.choices)
    action = models.CharField(max_length=100)  # e.g. "gmail.reply", "ai.analyze_email"
    config = models.JSONField(default=dict)     # action-specific params
    order = models.PositiveIntegerField()
    on_failure = models.CharField(max_length=20, default='stop')  # stop | continue | retry

    class Meta:
        ordering = ['order']
