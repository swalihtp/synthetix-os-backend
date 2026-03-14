from rest_framework import serializers
from .models import Integration


class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = [
            'id', 'provider', 'is_active', 'created_at'
        ]
        read_only_fields = fields