from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from system_admin.services.dashboard_statistics_service import (
    DashboardStatisticsService,
)
from system_admin.serializers.dashboard_statistics_serializer import (
    DashboardStatisticsSerializer,
)
from django.utils import timezone
from .permission import LambdaAuthentication
from workflows.models import (
    AIUsageLog,
    DailyAIUsageSnapshot,
    WorkflowExecution,
    EmailExecution,
)
from django.db.models import Q, Count
from rest_framework import status
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .serializers.email_activity_stream import EmailExecutionActivitySerializer
from accounts.models import User
from .serializers.user_registry_serializer import UserRegistrySerializer
from .throttles import AdminUserRegistryThrottle, AdminBuiltInAgentThrottle
from .filters import UserRegistryFilter, BuiltInAgentFilter
from .pagination import UserRegistryPagination, BuiltInAgentPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from agent.serializers import BuiltInAgentSerializer
from agent.models import BuiltInAgent
from workflows.serializers import WorkflowExecutionSerializer
from .serializers.admin_register_serializer import (
    AcceptInvitationSerializer,
    CreateAdminSerializer,
)
from .services.admin_services import AdminService
from rest_framework import generics
from accounts.permissions.rbac_permission import IsSystemAdmin


class DashboardStatisticsView(APIView):
    permission_classes = [IsSystemAdmin]

    def get(self, request):
        data = DashboardStatisticsService.get_statistics()

        serializer = DashboardStatisticsSerializer(data)

        return Response(serializer.data)


class GenerateAIUsageSnapshotView(APIView):
    authentication_classes = []
    permission_classes = [LambdaAuthentication]

    def post(self, request):

        today = timezone.now().date()

        stats = AIUsageLog.objects.aggregate(
            total_calls=Count("id"),
            intent_analysis_calls=Count("id", filter=Q(operation="INTENT_ANALYSIS")),
            reply_generation_calls=Count("id", filter=Q(operation="REPLY_GENERATION")),
            embedding_calls=Count("id", filter=Q(operation="EMBEDDING")),
            openrouter_calls=Count("id", filter=Q(provider="OPENROUTER")),
            gemini_calls=Count("id", filter=Q(provider="GEMINI")),
        )

        snapshot, created = DailyAIUsageSnapshot.objects.update_or_create(
            date=today,
            defaults=stats,
        )

        return Response(
            {
                "message": "AI usage snapshot generated",
                "created": created,
                "date": today,
            },
            status=status.HTTP_200_OK,
        )


class WorkflowExecutionStatsView(APIView):
    permission_classes = [IsSystemAdmin]  # Admin only

    def get(self, request):
        days = int(request.query_params.get("days", 7))
        since = timezone.now() - timedelta(days=days)

        qs = WorkflowExecution.objects.filter(started_at__gte=since)

        daily_stats = (
            qs.annotate(date=TruncDate("started_at"))
            .values("date")
            .annotate(
                total=Count("id"),
                success=Count("id", filter=Q(status="SUCCESS")),
                failed=Count("id", filter=Q(status="FAILED")),
                running=Count("id", filter=Q(status="RUNNING")),
            )
            .order_by("date")
        )

        daily = []
        for row in daily_stats:
            total = row["total"]
            daily.append(
                {
                    "date": row["date"],
                    "total": total,
                    "success": row["success"],
                    "failed": row["failed"],
                    "running": row["running"],
                    "success_rate": (
                        round((row["success"] / total) * 100, 1) if total else 0
                    ),
                    "failure_rate": (
                        round((row["failed"] / total) * 100, 1) if total else 0
                    ),
                }
            )

        summary = qs.aggregate(
            total=Count("id"),
            success=Count("id", filter=Q(status="SUCCESS")),
            failed=Count("id", filter=Q(status="FAILED")),
            running=Count("id", filter=Q(status="RUNNING")),
        )
        total = summary["total"] or 1
        summary["success_rate"] = round((summary["success"] / total) * 100, 1)
        summary["failure_rate"] = round((summary["failed"] / total) * 100, 1)

        return Response({"summary": summary, "daily": daily})


class AIUsageDashboardView(APIView):
    permission_classes = [IsSystemAdmin]
    def get(self, request):
        today = timezone.now().date()
        seven_days_ago = today - timedelta(days=6)

        today_logs = AIUsageLog.objects.filter(created_at__date=today).aggregate(
            total_calls=Count("id"),
            intent_analysis_calls=Count("id", filter=Q(operation="INTENT_ANALYSIS")),
            reply_generation_calls=Count("id", filter=Q(operation="REPLY_GENERATION")),
            embedding_calls=Count("id", filter=Q(operation="EMBEDDING")),
            openrouter_calls=Count("id", filter=Q(provider="OPENROUTER")),
            gemini_calls=Count("id", filter=Q(provider="GEMINI")),
        )

        snapshots = (
            DailyAIUsageSnapshot.objects.filter(date__range=[seven_days_ago, today])
            .order_by("date")
            .values(
                "date",
                "total_calls",
                "intent_analysis_calls",
                "reply_generation_calls",
                "embedding_calls",
                "openrouter_calls",
                "gemini_calls",
            )
        )

        trend = [
            {
                "date": str(s["date"]),
                "total_calls": s["total_calls"],
                "by_operation": {
                    "intent_analysis": s["intent_analysis_calls"],
                    "reply_generation": s["reply_generation_calls"],
                    "embedding": s["embedding_calls"],
                },
                "by_provider": {
                    "openrouter": s["openrouter_calls"],
                    "gemini": s["gemini_calls"],
                },
            }
            for s in snapshots
        ]

        model_breakdown = (
            AIUsageLog.objects.filter(created_at__date=today)
            .values("model_name", "provider")
            .annotate(calls=Count("id"))
            .order_by("-calls")
        )

        data = {
            "today": {
                "date": str(today),
                "total_calls": today_logs["total_calls"] or 0,
                "by_operation": {
                    "intent_analysis": today_logs["intent_analysis_calls"] or 0,
                    "reply_generation": today_logs["reply_generation_calls"] or 0,
                    "embedding": today_logs["embedding_calls"] or 0,
                },
                "by_provider": {
                    "openrouter": today_logs["openrouter_calls"] or 0,
                    "gemini": today_logs["gemini_calls"] or 0,
                },
                "by_model": [
                    {
                        "model_name": m["model_name"],
                        "provider": m["provider"],
                        "calls": m["calls"],
                    }
                    for m in model_breakdown
                ],
            },
            "last_7_days_trend": trend,
        }

        return Response(data)


class AdminEmailActivityStreamView(APIView):

    permission_classes = [IsSystemAdmin]

    def get(self, request):
        limit = min(int(request.query_params.get("limit", 20)), 100)
        result_filter = request.query_params.get("result")
        agent_id = request.query_params.get("agent_id")
        since_param = request.query_params.get("since")
        days = int(request.query_params.get("days", 7))
        intent_filter = request.query_params.get("intent")
        min_confidence = request.query_params.get("min_confidence")

        since = (
            timezone.datetime.fromisoformat(since_param)
            if since_param
            else timezone.now() - timedelta(days=days)
        )

        # ── Queryset — no agent_id filter by default ─────────────────────────
        qs = (
            EmailExecution.objects.filter(processed_at__gte=since)
            .select_related(
                "agent",
                "workflow_execution",
                "workflow_execution__workflow",
            )
            .order_by("-processed_at")
        )

        if agent_id:
            qs = qs.filter(agent_id=agent_id)

        if result_filter:
            qs = qs.filter(result=result_filter)

        if intent_filter:
            qs = qs.filter(detected_intent__icontains=intent_filter)

        if min_confidence:
            qs = qs.filter(confidence_score__gte=float(min_confidence))

        qs = qs[:limit]

        # ── Response ─────────────────────────────────────────────────────────
        serializer = EmailExecutionActivitySerializer(qs, many=True)
        return Response(
            {
                "count": len(serializer.data),
                "since": since,
                "activities": serializer.data,
            }
        )


class UserRegistryView(APIView):
    permission_classes = [IsSystemAdmin]
    throttle_classes = [AdminUserRegistryThrottle]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserRegistryFilter
    search_fields = ["email", "full_name"]
    ordering_fields = ["created_at", "email"]
    ordering = ["-created_at"]

    def filter_queryset(self, queryset):
        """Manually apply each backend (required for APIView)."""
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        queryset = User.objects.select_related("role").order_by("-created_at")

        # Apply search + filters + ordering
        queryset = self.filter_queryset(queryset)

        # Paginate
        paginator = UserRegistryPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = UserRegistrySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserDetailView(APIView):
    permission_classes = [IsSystemAdmin]
    throttle_classes = [AdminUserRegistryThrottle]

    def get(self, request, pk):
        user = get_object_or_404(
            User.objects.select_related("role").prefetch_related(
                "agents",
                "agents__workflows",
                "agents__workflows__execution_instances",
            ),
            pk=pk,
        )

        agent_count = user.agents.count()

        executions = WorkflowExecution.objects.filter(workflow__agent__user=user)

        workflow_executions = executions.count()

        workflow_executions_success = executions.filter(status="SUCCESS").count()

        workflow_executions_failure = executions.filter(status="FAILED").count()

        success_rate = 0

        if workflow_executions:
            success_rate = round(
                (workflow_executions_success / workflow_executions) * 100,
                2,
            )

        stats = []

        agent_count = {"label": "Agent Used", "value": agent_count}

        workflow_executions = {
            "label": "Workflow Execution",
            "value": workflow_executions,
        }
        success_rate = {"label": "Success Rate", "value": success_rate}

        stats = [agent_count, workflow_executions, success_rate]

        serializer = UserRegistrySerializer(user)

        executions_serializer = WorkflowExecutionSerializer(executions[:5], many=True)

        return Response(
            {
                **serializer.data,
                "stats": stats,
                "activities": executions_serializer.data,
            }
        )


class BuiltInAgentListView(APIView):
    permission_classes = [IsSystemAdmin]
    throttle_classes = [AdminBuiltInAgentThrottle]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BuiltInAgentFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def filter_queryset(self, queryset):
        """Manually apply each backend (required for APIView)."""
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        queryset = BuiltInAgent.objects.all().order_by("name")

        # Apply search + filters + ordering
        queryset = self.filter_queryset(queryset)

        # Paginate
        paginator = BuiltInAgentPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = BuiltInAgentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class BlockUserView(APIView):
    permission_classes = [IsSystemAdmin]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            return Response(
                {"detail": "You cannot block yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=["is_active"])

        return Response({"detail": "User blocked successfully."})


class ActivateUserView(APIView):
    permission_classes = [IsSystemAdmin]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response({"detail": "User activated successfully."})


class DeleteUserView(APIView):
    permission_classes = [IsSystemAdmin]

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            return Response(
                {"detail": "You cannot delete yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminCreateView(generics.GenericAPIView):
    permission_classes = [IsSystemAdmin]
    serializer_class = CreateAdminSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AdminService.create_admin(email=serializer.validated_data["email"])

        return Response(
            {"message": "Admin invitation sent successfully."},
            status=status.HTTP_201_CREATED,
        )


class AcceptInvitationView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AcceptInvitationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AdminService.accept_invitation(
            token=serializer.validated_data["token"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {"message": "Password set successfully."},
            status=status.HTTP_200_OK,
        )
