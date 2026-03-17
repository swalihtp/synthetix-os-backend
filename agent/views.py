from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Agent
from .serializers import AgentSerializer, AgentCreateSerializer


class AgentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Agent.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AgentCreateSerializer
        return AgentSerializer

    def get_serializer_context(self):
        return {'request': self.request}