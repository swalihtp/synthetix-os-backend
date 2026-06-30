import uuid
from django.db import models
from agent.models import Agent
from accounts.models import User


class Workflow(models.Model):

    TRIGGER_TYPES = [
        ("manual", "Manual"),
        ("event", "Event"),
        ("schedule", "Scheduled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="workflows")
    name = models.CharField(max_length=500)
    trigger_type = models.CharField(max_length=500, choices=TRIGGER_TYPES)
    trigger_config = models.JSONField(default=dict)
    prompt_template = models.TextField(blank=True, null=True, default="")
    schedule = models.CharField(
        max_length=250, blank=True, null=True
    )  # e.g. cron expression
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.trigger_type}"

class WorkflowExecution(models.Model):
    STATUS_CHOICES = [
        ("RUNNING", "RUNNING"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("PENDING","PENDING")
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow, on_delete=models.CASCADE, related_name="execution_instances"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RUNNING")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

class WorkflowForHumanReview(models.Model):
    HUMAN_CHOICES = [
        ("pending", "Pending"),
        ("accept", "Accept"),
        ("reject", "Reject"),
        ("manual_reply", "Manual Reply"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_body = models.TextField(null=True, blank=True)
    human_choice = models.CharField(
        max_length=100, choices=HUMAN_CHOICES, default="pending"
    )
    reply_body = models.TextField(null=True, blank=True)
    reply_subject = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.EmailField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

class AttachmentWithHumanReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attachment = models.FileField(upload_to="attachment_for_human_review/")
    human_review = models.ForeignKey(
        WorkflowForHumanReview, on_delete=models.CASCADE, related_name="attachments"
    )

class EmailExecutionResult(models.Model):
    RESULT_CHOICES = [
        ("AUTO_RESOLVED", "Auto Resolved"),
        ("HUMAN_REVIEW", "Human Review"),
        ("SKIPPED", "Skipped"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="execution_results"
    )

    workflow_execution = models.ForeignKey(
        WorkflowExecution, on_delete=models.CASCADE, related_name="results"
    )

    email_id = models.CharField(max_length=255)
    result = models.CharField(max_length=30, choices=RESULT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailExecution(models.Model):

    RESULT_CHOICES = [
        ("AUTO_RESOLVED", "Auto Resolved"),
        ("HUMAN_REVIEW", "Human Review"),
        ("SKIPPED", "Skipped"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="email_executions"
    )

    workflow_execution = models.OneToOneField(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name="email_execution",
    )

    # Gmail metadata
    email_id = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    thread_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Participants
    sender = models.EmailField(null=True, blank=True)
    recipient = models.EmailField(
        null=True,
        blank=True,
    )

    # Original email
    original_subject = models.TextField(
        null=True,
        blank=True,
    )
    original_body = models.TextField(
        null=True,
        blank=True,
    )

    # AI classification
    detected_intent = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
    )

    # Generated reply
    reply_subject = models.TextField(
        null=True,
        blank=True,
    )
    reply_body = models.TextField(
        null=True,
        blank=True,
    )

    # Final outcome
    result = models.CharField(
        max_length=30, choices=RESULT_CHOICES, blank=True, null=True
    )
    review_reason = models.TextField(
        null=True,
        blank=True,
    )
    processed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-processed_at"]
        indexes = [
            models.Index(fields=["email_id"]),
            models.Index(fields=["result"]),
            models.Index(fields=["processed_at"]),
        ]

class EmailAttachment(models.Model):

    STATUS_CHOICES = [
        ("PROCESSED", "Processed"),
        ("UNSUPPORTED", "Unsupported"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_execution = models.ForeignKey(
        EmailExecution,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    filename = models.CharField(max_length=500)
    mime_type = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=1000)
    extracted_text = models.TextField(
        null=True,
        blank=True,
    )
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

class AIUsageLog(models.Model):

    PROVIDERS = [
        ("OPENROUTER", "OPENROUTER"),
        ("GEMINI", "GEMINI"),
    ]

    OPERATIONS = [
        ("INTENT_ANALYSIS", "INTENT_ANALYSIS"),
        ("REPLY_GENERATION", "REPLY_GENERATION"),
        ("EMBEDDING", "EMBEDDING"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    workflow_execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name="ai_usage_logs",
    )

    provider = models.CharField(max_length=50)

    model_name = models.CharField(max_length=100)

    operation = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

class DailyAIUsageSnapshot(models.Model):

    date = models.DateField(unique=True)

    total_calls = models.IntegerField()

    intent_analysis_calls = models.IntegerField()

    reply_generation_calls = models.IntegerField()

    embedding_calls = models.IntegerField()

    openrouter_calls = models.IntegerField()

    gemini_calls = models.IntegerField()

class ResumeExecution(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_execution = models.OneToOneField(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name="resume_analyze_execution",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=10, null=True, blank=True)
    file_path = models.CharField(max_length=512, blank=True, null=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    raw_text = models.TextField(blank=True, null=True)
    resume_analysis = models.JSONField(blank=True, null=True)
    skill_evaluation = models.JSONField(blank=True, null=True)
    ats_score = models.JSONField(blank=True, null=True)
    feedback_report = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ResumeExecution({self.id}, {self.status})"

class MeetingSummaryExecution(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_execution = models.OneToOneField(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name="meeting_notes_execution",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_type = models.CharField(max_length=10, null=True, blank=True)
    file_path = models.CharField(max_length=512, blank=True, null=True)
    summary_style = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=250, choices=STATUS_CHOICES, null=True, blank=True
    )
    error_message = models.TextField(blank=True, null=True)
    raw_transcript = models.TextField(blank=True, null=True)
    topics = models.JSONField(blank=True, null=True)
    decisions = models.JSONField(blank=True, null=True)
    action_items = models.JSONField(blank=True, null=True)
    meeting_summary = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"MeetingSummaryExecution({self.id}, {self.status})"
