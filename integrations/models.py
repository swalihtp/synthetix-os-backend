import uuid
from django.db import models
from django.conf import settings


class Integration(models.Model):
    PROVIDERS = [
        ("gmail", "Gmail"),
        ("google_calendar", "Google Calendar"),
        ("slack", "Slack"),
        ("telegram", "Telegram"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="integrations"
    )
    provider = models.CharField(max_length=50, choices=PROVIDERS)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    last_gmail_history_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} - {self.user}"

    class Meta:
        unique_together = ["user", "provider"]

class ProcessedEmail(models.Model):
    id = models.UUIDField(primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='processed_emails',null=True, blank=True)
    message_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class V2Integration(models.Model):

    PROVIDER_CHOICES = [
        ("gmail", "Gmail"),
    ]

    AUTH_TYPE_CHOICES = [
        ("oauth2", "OAuth2"),
        ("api_key", "API Key"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="v2integrations"
    )
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    auth_type = models.CharField(max_length=50, choices=AUTH_TYPE_CHOICES)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    credentials = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "provider"]
        indexes = [
            models.Index(fields=["user", "provider"]),
            models.Index(fields=["is_active"]),
        ]

class GmailSync(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='gmail_sync')
    last_history_id = models.CharField(max_length=255, null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True)