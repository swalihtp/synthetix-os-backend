from rest_framework import serializers
from .models import Agent


class AgentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    goal_prompt = serializers.CharField()

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")