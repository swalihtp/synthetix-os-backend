from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from events.models import Event
from events.dispatcher import dispatch_event
from django.contrib.auth import get_user_model
from agent.models import Agent
import base64, json
from django.core.cache import cache
from integrations.gmail import get_gmail_service, get_email_details


User = get_user_model()


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
    

    message = request.data.get('message', {})
    data = message.get('data', '')

    try:
        decoded = base64.b64decode(data).decode('utf-8')
        payload = json.loads(decoded)
    except Exception:
        payload = request.data

    user_email = payload.get('emailAddress', '')

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

@api_view(['POST'])
@permission_classes([AllowAny])
def gmail_pubsub_webhook(request):

    try:
        print('something is comming  ------------------------------------------------------------------------------')
        message = request.data.get('message', {})
        data = message.get('data', '')
        message_id = message.get('messageId', '') or message.get('message_id', '')

        # Deduplicate — ignore if we already processed this Pub/Sub message
        if message_id:
            cache_key = f"pubsub_msg_{message_id}"
            if cache.get(cache_key):
                return Response({"message": "Already processed"}, status=200)
            cache.set(cache_key, True, timeout=300)  # 5 min TTL

        if data:
            decoded = base64.urlsafe_b64decode(data + '==').decode('utf-8')
            payload = json.loads(decoded)
        else:
            payload = request.data

        email_address = payload.get('emailAddress', '')
        history_id = payload.get('historyId', '')

        print(f"[Gmail Webhook] New email for: {email_address}")

        if not email_address:
            return Response({"message": "No email address"}, status=200)

        try:
            user = User.objects.get(email=email_address)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=200)

        email_data = fetch_latest_email(user, history_id)

        # Deduplicate by thread_id — don't process same email twice
        thread_id = email_data.get('thread_id', '')
        if thread_id:
            thread_cache_key = f"gmail_thread_{thread_id}"
            if cache.get(thread_cache_key):
                print(f"[Gmail] Already processed thread {thread_id}, skipping")
                return Response({"message": "Already processed"}, status=200)
            cache.set(thread_cache_key, True, timeout=600)  # 10 min TTL

        event = Event.objects.create(
            user=user,
            event_type='gmail.email_received',
            source='gmail',
            payload={
                'email_address': email_address,
                'history_id': history_id,
                'subject': email_data.get('subject', ''),
                'body': email_data.get('body', ''),
                'from': email_data.get('from', ''),
                'thread_id': thread_id,
                'message_id': email_data.get('message_id', ''),
            }
        )
        dispatch_event(event)
        return Response({"message": "Webhook received"}, status=200)

    except Exception as e:
        print(f"[Gmail Webhook] Error: {e}")
        return Response({"message": "Processed"}, status=200)

def fetch_latest_email(user, history_id: str) -> dict:
    """Fetch the latest unread email from Gmail API."""
    try:
        service = get_gmail_service(user)

        # Get list of recent messages
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=1
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return {}

        # Get full details of the latest message
        message_id = messages[0]['id']
        return get_email_details(service, message_id)

    except Exception as e:
        print(f"[Gmail] Could not fetch email: {e}")
        return {}
