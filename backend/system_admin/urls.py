from django.urls import path
from .views import (
    DashboardStatisticsView,
    GenerateAIUsageSnapshotView,
    WorkflowExecutionStatsView,
    AIUsageDashboardView,
    AdminEmailActivityStreamView,
    UserRegistryView,
    BuiltInAgentListView,
    UserDetailView,
    BlockUserView,
    ActivateUserView,
    DeleteUserView,
    AcceptInvitationView,
    AdminCreateView
)


urlpatterns = [
    path("dashboard/statistics/",DashboardStatisticsView.as_view(),name="dashboard-statistics"),
    path("analytics/snapshot/",GenerateAIUsageSnapshotView.as_view(), name="generate-ai-usage-snapshot"),
    path("workflows/stats/", WorkflowExecutionStatsView.as_view(), name="workflow-execution-statitics"),
    path("ai-usage/dashboard/", AIUsageDashboardView.as_view(), name="ai-usage-statitics"),
    path("email-activity/", AdminEmailActivityStreamView.as_view(), name="admin-email-activity-stream"),
    path('users/', UserRegistryView.as_view(), name='user-registry'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('builtin-agents/', BuiltInAgentListView.as_view(), name='builtin-agent-list'),
    path("users/<uuid:pk>/block/",BlockUserView.as_view(), name='block-user'),
    path("users/<uuid:pk>/activate/",ActivateUserView.as_view(), name='activate-user'),
    path("users/<uuid:pk>/delete/",DeleteUserView.as_view(), name='delete-user'),
    path("create-admin/",AdminCreateView.as_view(),name="create-admin",),
    path("accept-invite/",AcceptInvitationView.as_view(),name="accept-invite",),
]
