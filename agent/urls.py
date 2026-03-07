from django.urls import path
from .views import (
    AgentCreateView,
    AgentListView,
    AgentStatusUpdateView,
    GmailWebhookView,
)

app_name = "agents"

urlpatterns = [

    # -------------------------
    # Agent CRUD
    # -------------------------

    path("",AgentListView.as_view(),name="agent-list"),

    path("create/",AgentCreateView.as_view(),name="agent-create"),

    # path("<uuid:pk>/",AgentDetailView.as_view(),name="agent-detail"),

    path("<uuid:pk>/status/",AgentStatusUpdateView.as_view(),name="agent-status-update"),

    # path("<uuid:pk>/delete/",AgentDeleteView.as_view(),name="agent-delete"),

    # -------------------------
    # Agent Runs (Execution Logs)
    # -------------------------

    # path("<uuid:pk>/runs/",AgentRunListView.as_view(),name="agent-run-list"),

    # path("runs/<uuid:run_id>/",AgentRunDetailView.as_view(),name="agent-run-detail"),

    # -------------------------
    # Webhooks
    # -------------------------

    path("webhooks/gmail/",GmailWebhookView.as_view(),name="gmail-webhook"),
]