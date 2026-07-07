from django.db.models import Count, Q
from accounts.models import User
from agent.models import BuiltInAgent
from workflows.models import WorkflowExecution


class DashboardStatisticsService:

    @staticmethod
    def get_statistics():
        
        user_stats = {
            "total": User.objects.count(),
            "active": User.objects.filter(
                is_active=True,
                is_verified=True,
            ).count(),
        }

        agent_stats = {"total": BuiltInAgent.objects.count()}

        execution_stats = WorkflowExecution.objects.aggregate(
            total=Count("id"),
            success=Count("id", filter=Q(status="SUCCESS")),
            failed=Count("id", filter=Q(status="FAILED")),
            running=Count("id", filter=Q(status="RUNNING")),
        )

        return {
            "users": user_stats,
            "agents": agent_stats,
            "workflow_executions": execution_stats,
        }
