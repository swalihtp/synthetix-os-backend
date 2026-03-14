import uuid
from django.db import models
from django.conf import settings

class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agents',null=True, blank=True)
    name = models.CharField(max_length=200,null=True, blank=True)
    description = models.TextField(blank=True,null=True)
    prompt = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user})"

    class Meta:
        ordering = ['-created_at']