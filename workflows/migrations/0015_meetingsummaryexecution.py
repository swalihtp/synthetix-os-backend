import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("workflows", "0014_resumeexecution"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingSummaryExecution",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, blank=True, null=True),
                ),
                ("file_name", models.CharField(blank=True, max_length=255, null=True)),
                ("file_type", models.CharField(blank=True, max_length=10, null=True)),
                ("file_path", models.CharField(blank=True, max_length=512, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending", "Pending"),
                            ("processing", "Processing"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        max_length=250,
                        null=True,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                ("raw_transcript", models.TextField(blank=True, null=True)),
                ("topics", models.JSONField(blank=True, null=True)),
                ("decisions", models.JSONField(blank=True, null=True)),
                ("action_items", models.JSONField(blank=True, null=True)),
                ("meeting_summary", models.JSONField(blank=True, null=True)),
                (
                    "workflow_execution",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meeting_notes_execution",
                        to="workflows.workflowexecution",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
