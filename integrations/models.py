import uuid
from django.db import models
from django.conf import settings

class Integration(models.Model):
    PROVIDERS = [
        ('gmail', 'Gmail'),
        ('google_calendar', 'Google Calendar'),
        ('slack', 'Slack'),
        ('telegram', 'Telegram'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='integrations')
    provider = models.CharField(max_length=50, choices=PROVIDERS)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} - {self.user}"

    class Meta:
        unique_together = ['user', 'provider']
