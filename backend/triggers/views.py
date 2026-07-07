from rest_framework.decorators import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import base64, json
from django.core.cache import cache
import logging
from workflows.tasks import process_gmail_notification_task

logger = logging.getLogger(__name__)

User = get_user_model()

class NewGmailPubSubWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            message = request.data.get("message", {})
            encoded_data = message.get("data")
            pubsub_msg_id = message.get("messageId") or message.get("message_id")


            if not encoded_data:
                return Response({"message": "No data"}, status=200)

            payload = json.loads(
                base64.urlsafe_b64decode(encoded_data + "==").decode("utf-8")
            )
            payload['pubsub_msg_id'] = pubsub_msg_id

            process_gmail_notification_task.delay({'payload':payload})

            return Response({"message": "Accepted"}, status=200)

        except Exception as e:
            logger.exception("gmail webhook failed", extra={"payload": request.data})

            # Always return 200 to Pub/Sub
            return Response({"message": "Accepted"}, status=200)
