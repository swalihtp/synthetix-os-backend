from rest_framework import serializers
from agent.models import Agent
from workflows.models import EmailExecution, WorkflowExecution, Workflow


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ["id", "name"]


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ["id", "name", "trigger_type", "is_active"]


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    workflow = WorkflowSerializer(read_only=True)

    class Meta:
        model = WorkflowExecution
        fields = [
            "id",
            "status",
            "started_at",
            "ended_at",
            "error_message",
            "workflow",
        ]


class EmailExecutionActivitySerializer(serializers.ModelSerializer):
    agent = AgentSerializer(read_only=True)
    workflow_execution = WorkflowExecutionSerializer(read_only=True)

    class Meta:
        model = EmailExecution
        fields = [
            "id",
            "email_id",
            "thread_id",
            "sender",
            "recipient",
            "original_subject",
            "detected_intent",
            "confidence_score",
            "result",
            "review_reason",
            "processed_at",
            "agent",
            "workflow_execution",
        ]
        # original_body / reply_body excluded — too heavy for a stream view
