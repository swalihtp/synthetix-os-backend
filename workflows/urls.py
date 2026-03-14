from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, WorkflowRunViewSet

router = DefaultRouter()
router.register(r'runs', WorkflowRunViewSet, basename='workflowrun')
router.register(r'', WorkflowViewSet, basename='workflow')

urlpatterns = [
    path('', include(router.urls)),
]