from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Workflow, WorkflowRun
from .serializers import (
    WorkflowSerializer,
    WorkflowCreateSerializer,
    WorkflowRunSerializer,
)


class WorkflowViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(
            agent__user=self.request.user
        ).prefetch_related('steps')

    def get_serializer_class(self):
        if self.action == 'create':
            return WorkflowCreateSerializer
        return WorkflowSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    @action(detail=True, methods=['get'], url_path='runs')
    def runs(self, request, pk=None):
        workflow = self.get_object()
        runs = WorkflowRun.objects.filter(
            workflow=workflow
        ).order_by('-started_at')
        serializer = WorkflowRunSerializer(runs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='trigger')
    def trigger(self, request, pk=None):
        """Manually trigger a workflow from the API."""
        from events.models import Event
        from events.dispatcher import dispatch_event

        workflow = self.get_object()
        event = Event.objects.create(
            user=request.user,
            event_type=workflow.trigger_type,
            source='manual',
            payload=request.data,
        )
        dispatch_event(event)
        return Response({
            'message': 'Workflow triggered',
            'event_id': str(event.id)
        })


class WorkflowRunViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkflowRunSerializer

    def get_queryset(self):
        return WorkflowRun.objects.filter(
            workflow__agent__user=self.request.user
        ).order_by('-started_at')