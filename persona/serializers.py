from rest_framework import serializers
from .models import UserPersona


class UserPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPersona
        fields = '__all__'
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at'
        ]