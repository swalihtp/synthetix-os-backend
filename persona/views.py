from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import UserPersona
from .serializers import UserPersonaSerializer


class UserPersonaViewSet(viewsets.ModelViewSet):
    serializer_class = UserPersonaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserPersona.objects.filter(user=self.request.user)

    def get_object(self):
        persona, created = UserPersona.objects.get_or_create(user=self.request.user)
        return persona

    def list(self, request, *args, **kwargs):
        """
        Get current user's persona.
        """

        persona = self.get_object()
        serializer = self.get_serializer(persona)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create or update persona.
        """

        persona, created = UserPersona.objects.get_or_create(user=request.user)

        serializer = self.get_serializer(persona, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        update_completion_percentage(persona)

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        persona = self.get_object()

        serializer = self.get_serializer(persona, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        update_completion_percentage(persona)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        persona = self.get_object()
        persona.delete()

        return Response({"message": "Persona deleted successfully"})

    @action(detail=False, methods=["get"])
    def completion(self, request):
        """
        Get completion status.
        """

        persona = self.get_object()

        return Response(
            {
                "completed": persona.completed,
                "completion_percentage": persona.completion_percentage,
            }
        )

    @action(detail=False, methods=["get"])
    def metadata(self, request):
        return Response(
            {
                "role_choices": [
                    {"label": label, "value": value}
                    for value, label in UserPersona.ROLE_CHOICES
                ],
                "ai_tone_choices": [
                    {"label": label, "value": value}
                    for value, label in UserPersona.AI_TONE_CHOICES
                ],
                "response_style_choices": [
                    {"label": label, "value": value}
                    for value, label in UserPersona.RESPONSE_STYLE_CHOICES
                ],
                "priority_choices": [
                    {"label": label, "value": value}
                    for value, label in UserPersona.PRIORITY_CHOICES
                ],
            }
        )


def update_completion_percentage(persona):
    fields = [
        persona.display_name,
        persona.role,
        persona.industry,
        persona.primary_goals,
        persona.business_description,
        persona.ai_avoidances,
        persona.communication_style,
        persona.common_messages,
        persona.workday_improvements,
        persona.important_documents,
        persona.brand_guidelines,
        persona.long_term_memory,
        persona.privacy_preferences,
    ]

    filled_fields = len([field for field in fields if field not in [None, "", [], {}]])

    total_fields = len(fields)

    percentage = int((filled_fields / total_fields) * 100)

    persona.completion_percentage = percentage

    persona.completed = percentage >= 80
    persona.save()
