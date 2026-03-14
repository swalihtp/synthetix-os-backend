from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from events.models import Event
from events.dispatcher import dispatch_event


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_trigger(request, path):
    """Generic webhook receiver — creates an Event and dispatches it."""
    user_id = request.data.get('user_id')
    if not user_id:
        return Response(
            {"error": "user_id required in payload"},
            status=status.HTTP_400_BAD_REQUEST
        )

    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    event = Event.objects.create(
        user=user,
        event_type=f"webhook.{path}",
        source="webhook",
        payload=request.data,
    )
    dispatch_event(event)
    return Response({"message": "Event received", "event_id": str(event.id)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_trigger(request, agent_id):
    """Manual trigger — authenticated user fires a workflow directly."""
    from agent.models import Agent
    try:
        agent = Agent.objects.get(id=agent_id, user=request.user)
    except Agent.DoesNotExist:
        return Response({"error": "Agent not found"}, status=404)

    event = Event.objects.create(
        user=request.user,
        event_type="api.trigger",
        source="api",
        payload=request.data,
    )
    dispatch_event(event)
    return Response({"message": "Workflow triggered", "event_id": str(event.id)})


@api_view(['POST'])
@permission_classes([AllowAny])
def gmail_webhook(request):
    """Gmail Pub/Sub push notification receiver."""
    import base64, json

    message = request.data.get('message', {})
    data = message.get('data', '')

    try:
        decoded = base64.b64decode(data).decode('utf-8')
        payload = json.loads(decoded)
    except Exception:
        payload = request.data

    user_email = payload.get('emailAddress', '')

    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return Response({"message": "User not found, ignoring"})

    event = Event.objects.create(
        user=user,
        event_type="gmail.email_received",
        source="gmail",
        payload=payload,
    )
    dispatch_event(event)
    return Response({"message": "Gmail event received"})
