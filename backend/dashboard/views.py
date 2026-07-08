from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import DashboardService
from .serializers import DashboardSerializer
import logging

logger = logging.getLogger(__name__)


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            service = DashboardService(request.user)

            dashboard_data = service.get_dashboard()

            serializer = DashboardSerializer(dashboard_data)

            return Response(serializer.data)

        except Exception:
            logger.exception(
                "Failed to load dashboard for user %s",
                request.user.id,
            )

            return Response(
                {"detail": "Unable to load dashboard."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
