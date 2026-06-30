from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet, BuiltInAgentViewSet, EmailAgentDashboardAPIView

router = DefaultRouter()
router.register(r"builtin", BuiltInAgentViewSet, basename="builtin-agent")
router.register(r"", AgentViewSet, basename="agent")

urlpatterns = [
    path(
        "<uuid:agent_id>/dashboard/",
        EmailAgentDashboardAPIView.as_view(),
        name="email-agent-dashboard",
    ),
    path("", include(router.urls)),
]
