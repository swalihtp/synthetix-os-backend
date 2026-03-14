from rest_framework import serializers
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'description', 'prompt',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['name', 'description', 'prompt']

    def create(self, validated_data):
        user = self.context['request'].user
        return Agent.objects.create(user=user, **validated_data)