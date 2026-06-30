from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmailExecutionViewSet,
    ResumeExecutionViewSet,
    MeetingSummaryExecutionViewSet,
    MeetingNotesExecutionView,
    WorkflowViewSet,
    ResumeAnalysisExecutionView,
    ResumeAnalysisRetryView,
    MeetingSummaryRetryView,
)
router = DefaultRouter()
router.register(r'email-executions', EmailExecutionViewSet, basename='email-executions')
router.register(r"resume-executions", ResumeExecutionViewSet, basename="resume-execution")
router.register(r"meeting-summary-executions", MeetingSummaryExecutionViewSet, basename="meeting-summary-execution")
router.register(r"", WorkflowViewSet, basename="workflow")

urlpatterns = [
    path("resume-executions/analyze/", ResumeAnalysisExecutionView.as_view(), name="resume-analysis-execute"),
    path("resume-executions/retry/", ResumeAnalysisRetryView.as_view(), name="resume-analysis-retry"),
    path("meeting-notes-executions/analyze/", MeetingNotesExecutionView.as_view(), name="meeting-notes-execute"),
    path("meeting-summary-executions/retry/", MeetingSummaryRetryView.as_view(), name="meeting-summary-retry"),
    path("", include(router.urls)),
]
