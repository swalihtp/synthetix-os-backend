import uuid
from django.db import models
from django.conf import settings
from accounts.models import User


class BuiltInAgent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    prompt_template = models.TextField()
    workflow_configuration = models.JSONField(
        default=dict, help_text="Stores trigger_type and step definitions"
    )
    input_schema = models.JSONField(blank=True, null=True)
    required_integrations = models.JSONField(blank=True, null=True)
    capabilities = models.JSONField(blank=True, null=True)
    tools = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agents",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    prompt = models.TextField(null=True, blank=True)
    agent_schema = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    template = models.ForeignKey(
        BuiltInAgent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instances",
    )

    def __str__(self):
        return f"{self.name} ({self.user})"

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_agent_per_user"
            )
        ]


class AgentDocuments(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    agent = models.ForeignKey(Agent,on_delete=models.CASCADE,related_name="documents",)

    document = models.FileField(upload_to="agent-documents/")

    original_name = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending",null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)


class S3MarketIntelligenceReport(models.Model):
    agent = models.ForeignKey(
        Agent,
        related_name="market_intelligence_reports",
        on_delete=models.CASCADE,
    )

    s3_key = models.CharField(max_length=550)

    s3_url = models.URLField(max_length=1000)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.agent} - {self.created_at}"


class AgentExecution(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="exicution_instances"
    )

    status = models.CharField(max_length=50)

    current_step = models.CharField(max_length=255, null=True, blank=True)

    market_research = models.TextField(null=True, blank=True)
    competitors = models.TextField(null=True, blank=True)
    trends = models.TextField(null=True, blank=True)
    sentiment = models.TextField(null=True, blank=True)
    swot = models.TextField(null=True, blank=True)

    scraped_data_from_compony_website = models.TextField(null=True, blank=True)
    scraped_data_from_competitor_websites = models.TextField(null=True, blank=True)

    final_report = models.TextField(null=True, blank=True)

    report_path = models.TextField(null=True, blank=True)

    s3_url = models.TextField(null=True, blank=True)

    error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
