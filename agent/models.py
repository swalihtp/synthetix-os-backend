import uuid
from django.db import models
from django.conf import settings



class Agent(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agents",
    )

    name = models.CharField(max_length=150)
    goal_prompt = models.TextField(help_text="Core mission of the agent")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    llm_model = models.CharField(
        max_length=100,
        default="gpt-4o",
        help_text="LLM model used for reasoning",
    )

    temperature = models.FloatField(default=0.3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
class AgentTrigger(models.Model):
    class TriggerType(models.TextChoices):
        SLACK_MESSAGE = "slack_message", "Slack Message"
        EMAIL_RECEIVED = "email_received", "Email Received"
        WEBHOOK = "webhook", "Webhook"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="triggers",
    )

    trigger_type = models.CharField(
        max_length=50,
        choices=TriggerType.choices,
    )

    config = models.JSONField(
        default=dict,
        help_text="Trigger configuration (channel_id, email filters, etc.)",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["trigger_type", "is_active"]),
        ]

class AgentAction(models.Model):
    class ActionType(models.TextChoices):
        SEND_SLACK = "send_slack", "Send Slack Message"
        SEND_EMAIL = "send_email", "Send Email"
        CREATE_STRIPE_INVOICE = "create_stripe_invoice", "Create Stripe Invoice"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="actions",
    )

    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
    )

    config = models.JSONField(
        default=dict,
        help_text="Action configuration (channel, template, etc.)",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
class AgentRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="runs",
    )

    trigger_event = models.JSONField(default=dict)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    error_message = models.TextField(blank=True, null=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["agent", "status"]),
        ]
        ordering = ["-created_at"]
        
class AgentStep(models.Model):
    run = models.ForeignKey(
        AgentRun,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    step_order = models.PositiveIntegerField()

    thought = models.TextField(blank=True, null=True)
    action_taken = models.TextField(blank=True, null=True)
    action_response = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["step_order"]
        
class ToolConnection(models.Model):
    class ToolType(models.TextChoices):
        SLACK = "slack", "Slack"
        GMAIL = "gmail", "Gmail"
        STRIPE = "stripe", "Stripe"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tool_connections",
    )

    tool_type = models.CharField(
        max_length=50,
        choices=ToolType.choices,
    )

    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    
