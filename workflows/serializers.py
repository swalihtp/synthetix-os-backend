from rest_framework import serializers
from .models import Workflow, WorkflowStep, WorkflowRun


class WorkflowStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStep
        fields = ['id', 'step_type', 'action', 'config', 'order', 'on_failure']
        read_only_fields = ['id']


class WorkflowSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True, read_only=True)

    class Meta:
        model = Workflow
        fields = [
            'id', 'agent', 'name', 'trigger_type',
            'trigger_config', 'is_active', 'created_at', 'steps'
        ]
        read_only_fields = ['id', 'created_at']


class WorkflowCreateSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True)

    class Meta:
        model = Workflow
        fields = ['agent', 'name', 'trigger_type', 'trigger_config', 'steps']

    def validate_agent(self, agent):
        if agent.user != self.context['request'].user:
            raise serializers.ValidationError("Agent not found.")
        return agent

    def create(self, validated_data):
        steps_data = validated_data.pop('steps')
        workflow = Workflow.objects.create(**validated_data)
        for step_data in steps_data:
            WorkflowStep.objects.create(workflow=workflow, **step_data)
        return workflow


class WorkflowRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowRun
        fields = [
            'id', 'workflow', 'event', 'status',
            'context', 'current_step', 'error',
            'started_at', 'finished_at'
        ]
        read_only_fields = fields