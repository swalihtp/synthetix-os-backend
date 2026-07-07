from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Agent, BuiltInAgent
from .serializers import AgentSerializer, AgentCreateSerializer, BuiltInAgentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from workflows.models import EmailExecutionResult, WorkflowForHumanReview
from workflows.serializers import EmailAgentDashboardSerializer
from rest_framework import filters
from .pagination import BuiltInAgentPagination

class AgentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Agent.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return AgentCreateSerializer
        return AgentSerializer

    def get_serializer_context(self):
        return {"request": self.request}


class BuiltInAgentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = BuiltInAgent.objects.all()
    serializer_class = BuiltInAgentSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = BuiltInAgentPagination
    search_fields = [
        "name",
        "description",
    ]


class EmailAgentDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, agent_id):

        agent = get_object_or_404(Agent, id=agent_id, user=request.user)
        processed_emails = EmailExecutionResult.objects.filter(agent=agent).count()

        human_reviews = EmailExecutionResult.objects.filter(
            agent=agent, result="HUMAN_REVIEW"
        ).count()

        pending_reviews = WorkflowForHumanReview.objects.filter(
            agent=agent, human_choice="pending"
        ).count()

        auto_resolved = EmailExecutionResult.objects.filter(
            agent=agent, result="AUTO_RESOLVED"
        ).count()

        auto_resolved_percentage = (
            round((auto_resolved / processed_emails) * 100, 2)
            if processed_emails > 0
            else 0
        )

        data = {
            "agent": AgentSerializer(agent).data,
            "stats": {
                "processed_emails": processed_emails,
                "human_reviews": human_reviews,
                "pending_reviews": pending_reviews,
                "auto_resolved_percentage": auto_resolved_percentage,
            },
        }

        serializer = EmailAgentDashboardSerializer(data)

        return Response(serializer.data)
