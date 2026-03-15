import os
import base64
import json
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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
        providers = ['gmail', 'google_calendar', 'slack', 'telegram']
        connected = Integration.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('provider', flat=True)
        return Response({
            provider: provider in connected
            for provider in providers
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gmail_connect(request):
    """Step 1 — return Google OAuth consent screen URL."""
    from google_auth_oauthlib.flow import Flow

    # Encode user_id inside state
    state_data = base64.urlsafe_b64encode(
        json.dumps({"user_id": str(request.user.id)}).encode()
    ).decode()

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URI")],
            }
        },
        scopes=[
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/userinfo.email',
        ],
    )
    flow.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=state_data,
        code_challenge_method=None,  # disable PKCE
    )

    # Remove code_challenge from URL if present
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
    parsed = urlparse(auth_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop('code_challenge', None)
    params.pop('code_challenge_method', None)
    clean_params = {k: v[0] for k, v in params.items()}
    clean_url = urlunparse(parsed._replace(query=urlencode(clean_params)))

    return Response({"auth_url": clean_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def gmail_callback(request):
    """Step 2 — Google redirects here, exchange code for tokens."""
    from google_auth_oauthlib.flow import Flow
    from django.contrib.auth import get_user_model
    from requests_oauthlib import OAuth2Session

    User = get_user_model()

    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code:
        return Response({"error": "No code received from Google."}, status=400)

    if not state:
        return Response({"error": "No state received from Google."}, status=400)

    # Decode user_id from state
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        user_id = state_data.get("user_id")
    except Exception:
        return Response({"error": "Invalid state parameter."}, status=400)

    if not user_id:
        return Response({"error": "User ID missing from state."}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

    # Exchange code for tokens manually without PKCE
    try:
        import requests as req
        token_response = req.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': os.environ.get("GOOGLE_CLIENT_ID"),
                'client_secret': os.environ.get("GOOGLE_CLIENT_SECRET"),
                'redirect_uri': os.environ.get("GOOGLE_REDIRECT_URI"),
                'grant_type': 'authorization_code',
            }
        )
        token_data = token_response.json()

        if 'error' in token_data:
            return Response(
                {"error": f"Token exchange failed: {token_data['error_description']}"},
                status=400
            )

        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token', '')

    except Exception as e:
        return Response({"error": f"Token exchange failed: {str(e)}"}, status=400)

    # Save tokens to Integration model
    Integration.objects.update_or_create(
        user=user,
        provider='gmail',
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'is_active': True,
        }
    )

    return Response({
        "message": "Gmail connected successfully!",
        "user": user.email,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gmail_watch(request):
    """Register Gmail push notifications."""
    from integrations.gmail_watch import register_gmail_watch
    try:
        result = register_gmail_watch(request.user)
        return Response({
            "message": "Gmail watch registered successfully.",
            "expiration": result.get('expiration'),
            "historyId": result.get('historyId'),
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)