from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from agent.models import Agent, BuiltInAgent, AgentExecution
from workflows.models import (
    Workflow,
    WorkflowExecution,
    ResumeExecution,
    MeetingSummaryExecution,
    EmailExecution,
    AIUsageLog,
)


def get_agent_count(user):
    return Agent.objects.filter(user=user).count()


def get_builtin_agent_count():
    return BuiltInAgent.objects.count()


def get_workflow_count(user):
    return Workflow.objects.filter(agent__user=user).count()


def get_running_workflow_count(user):
    return WorkflowExecution.objects.filter(
        workflow__agent__user=user,
        status="RUNNING",
    ).count()
    
    
def get_completed_today(user):
    today = timezone.now().date()

    return WorkflowExecution.objects.filter(
        workflow__agent__user=user,
        status="SUCCESS",
        started_at__date=today,
    ).count()


def get_failed_today(user):
    today = timezone.now().date()

    return WorkflowExecution.objects.filter(
        workflow__agent__user=user,
        status="FAILED",
        started_at__date=today,
    ).count()
    
    
def get_ai_calls_today(user):
    today = timezone.now().date()

    return AIUsageLog.objects.filter(
        workflow_execution__workflow__agent__user=user,
        created_at__date=today,
    ).count()
    
    
def get_resume_analysis_today(user):
    today = timezone.now().date()

    return ResumeExecution.objects.filter(
        workflow_execution__workflow__agent__user=user,
        created_at__date=today,
        status="completed",
    ).count()
    
def get_meeting_summary_today(user):
    today = timezone.now().date()

    return MeetingSummaryExecution.objects.filter(
        workflow_execution__workflow__agent__user=user,
        created_at__date=today,
        status="completed",
    ).count()
    
def get_email_processed_today(user):
    today = timezone.now().date()

    return EmailExecution.objects.filter(
        agent__user=user,
        processed_at__date=today,
    ).count()
    
def get_workflow_status_summary(user):
    queryset = (
        WorkflowExecution.objects
        .filter(workflow__agent__user=user)
        .values("status")
        .annotate(total=Count("id"))
    )

    summary = {
        "SUCCESS": 0,
        "FAILED": 0,
        "RUNNING": 0,
        "PENDING": 0,
    }

    for item in queryset:
        summary[item["status"]] = item["total"]

    return summary


def get_application_usage(user):

    return {
        "Resume Analyzer": ResumeExecution.objects.filter(
            workflow_execution__workflow__agent__user=user
        ).count(),

        "Meeting Summarizer": MeetingSummaryExecution.objects.filter(
            workflow_execution__workflow__agent__user=user
        ).count(),

        "Email Automation": EmailExecution.objects.filter(
            agent__user=user
        ).count(),

        "Market Intelligence": AgentExecution.objects.filter(
            user=user
        ).count(),
    }
    
def get_recent_resume_executions(user, limit=5):
    return ResumeExecution.objects.filter(
        workflow_execution__workflow__agent__user=user
    ).select_related(
        "workflow_execution"
    ).order_by("-updated_at")[:limit]
    
    
def get_recent_meeting_executions(user, limit=5):
    return MeetingSummaryExecution.objects.filter(
        workflow_execution__workflow__agent__user=user
    ).select_related(
        "workflow_execution"
    ).order_by("-updated_at")[:limit]
    
def get_recent_email_executions(user, limit=5):
    return EmailExecution.objects.filter(
        agent__user=user
    ).select_related(
        "workflow_execution"
    ).order_by("-processed_at")[:limit]
    
    
def get_builtin_agents():
    return BuiltInAgent.objects.all()
