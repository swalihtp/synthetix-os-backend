from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Integration
from .serializers import IntegrationSerializer


class IntegrationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IntegrationSerializer

    def get_queryset(self):
        return Integration.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='status')
    def connection_status(self, request):
        """Show which services are connected."""
        providers = ['gmail', 'google_calendar', 'slack', 'telegram']
        connected = Integration.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('provider', flat=True)

        return Response({
            provider: provider in connected
            for provider in providers
        })