from django.db import models

import uuid
from django.conf import settings
from django.db import models


class UserPersona(models.Model):
    ROLE_CHOICES = [
        ("freelancer", "Freelancer"),
        ("business_owner", "Business Owner"),
        ("developer", "Developer"),
        ("designer", "Designer"),
        ("marketer", "Marketer"),
        ("student", "Student"),
        ("other", "Other"),
    ]

    RESPONSE_STYLE_CHOICES = [
        ("concise", "Concise"),
        ("detailed", "Detailed"),
    ]

    AI_TONE_CHOICES = [
        ("formal", "Formal"),
        ("casual", "Casual"),
        ("friendly", "Friendly"),
        ("professional", "Professional"),
    ]

    PRIORITY_CHOICES = [
        ("speed", "Speed"),
        ("accuracy", "Accuracy"),
        ("balanced", "Balanced"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="persona"
    )

    # Basic Information
    display_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default="other")
    industry = models.CharField(max_length=255, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    primary_goals = models.TextField(blank=True, null=True)

    # Work & Business
    business_description = models.TextField(blank=True, null=True)

    # AI Personalization
    ai_tone = models.CharField(
        max_length=50, choices=AI_TONE_CHOICES, default="professional"
    )

    response_style = models.CharField(
        max_length=50, choices=RESPONSE_STYLE_CHOICES, default="detailed"
    )
    ai_priority = models.CharField(
        max_length=50, choices=PRIORITY_CHOICES, default="balanced"
    )

    ai_avoidances = models.TextField(blank=True, null=True)

    # Communication & Productivity
    communication_style = models.TextField(blank=True, null=True)
    common_messages = models.TextField(blank=True, null=True)
    manages_projects = models.BooleanField(default=False)
    workday_improvements = models.TextField(blank=True, null=True)

    # Knowledge & Context
    important_documents = models.TextField(blank=True, null=True)
    brand_guidelines = models.TextField(blank=True, null=True)
    long_term_memory = models.TextField(blank=True, null=True)
    privacy_preferences = models.TextField(blank=True, null=True)

    # Metadata
    completed = models.BooleanField(default=False)
    completion_percentage = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Persona"
