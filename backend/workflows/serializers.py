from rest_framework import serializers
from .models import (
    Workflow,
    WorkflowForHumanReview,
    AttachmentWithHumanReview,
    EmailAttachment,
    EmailExecution,
    WorkflowExecution,
)
from agent.serializers import AgentSerializer
import boto3
from django.conf import settings
from .models import ResumeExecution, MeetingSummaryExecution


class WorkflowSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="agent.name", read_only=True)

    class Meta:
        model = Workflow
        fields = [
            "id",
            "agent",
            "name",
            "prompt_template",
            "trigger_type",
            "trigger_config",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class WorkflowCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workflow
        fields = ["agent", "name", "trigger_type", "trigger_config"]

    def validate_agent(self, agent):
        if agent.user != self.context["request"].user:
            raise serializers.ValidationError("Agent not found.")
        return agent

    def create(self, validated_data):
        workflow = Workflow.objects.create(**validated_data)
        return workflow

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentWithHumanReview
        fields = ["id", "attachment"]

class HumanReviewForGmail(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowForHumanReview
        fields = "__all__"

class DashboardStatsSerializer(serializers.Serializer):
    processed_emails = serializers.IntegerField()
    human_reviews = serializers.IntegerField()
    pending_reviews = serializers.IntegerField()
    auto_resolved_percentage = serializers.FloatField()

class EmailAgentDashboardSerializer(serializers.Serializer):
    agent = AgentSerializer()
    stats = DashboardStatsSerializer()

class EmailAttachmentSerializer(serializers.ModelSerializer):
    attachment = serializers.SerializerMethodField()

    class Meta:
        model = EmailAttachment
        fields = ["id", "filename", "attachment"]

    def get_attachment(self, obj):
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": obj.s3_key},
                ExpiresIn=3600,
            )
        except Exception:
            return obj.s3_key

class EmailExecutionListSerializer(serializers.ModelSerializer):

    subject = serializers.CharField(source="original_subject")
    reason = serializers.CharField(source="review_reason")
    time = serializers.DateTimeField(source="processed_at")

    priority = serializers.SerializerMethodField()

    class Meta:
        model = EmailExecution
        fields = [
            "id",
            "subject",
            "priority",
            "sender",
            "reason",
            "time",
            "result",
        ]

    def get_priority(self, obj):
        score = obj.confidence_score
        if score is None:
            return "MEDIUM"
        if score < 0.4:
            return "CRITICAL"
        if score < 0.7:
            return "HIGH"
        return "MEDIUM"

class EmailExecutionDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for the detail page.
    """

    email_body = serializers.CharField(source="original_body")
    reason = serializers.CharField(source="review_reason")
    human_choice = serializers.CharField(source="result")
    attachments = EmailAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = EmailExecution
        fields = [
            "id",
            "sender",
            "human_choice",
            "reason",
            "email_body",
            "reply_subject",
            "reply_body",
            "attachments",
            "result",
        ]

class WorkflowExecutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowExecution
        fields = "__all__"
        read_only_fields = [
            "id",
            "started_at",
            "ended_at",
        ]

class ResumeExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeExecution
        fields = "__all__"


class MeetingSummaryExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingSummaryExecution
        fields = "__all__"

class MeetingNotesInputSerializer(serializers.Serializer):
    file = serializers.FileField()
    summary_style = serializers.ChoiceField(
        choices=["concise", "detailed", "executive"],
        required=False,
        default="concise",
    )

class ResumeAnalysisInputSerializer(serializers.Serializer):
    file = serializers.FileField()
    job_title = serializers.CharField(max_length=255)
    job_description = serializers.CharField()


class RetryExecutionSerializer(serializers.Serializer):
    execution_id = serializers.UUIDField()
