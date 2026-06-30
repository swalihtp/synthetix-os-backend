import os
import base64
import json
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Integration
from .serializers import IntegrationSerializer
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow
import requests as req
from integrations.gmail_watch import register_gmail_watch
from google_auth_oauthlib.flow import Flow
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication


User=get_user_model()


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


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def gmail_connect(request):
    """Step 1 — return Google OAuth consent screen URL with agent_id in state."""
    
    agent_id = request.data.get('agent_id')  # ✅ Get agent_id from request
    
    if not agent_id:
        return Response({"error": "agent_id is required"}, status=400)
    
    # ✅ Encode BOTH user_id AND agent_id in state
    state_data = base64.urlsafe_b64encode(
        json.dumps({
            "user_id": str(request.user.id),
            "agent_id": agent_id  # ✅ Include this
        }).encode()
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
    # print('flow object:', flow.__dict__)
    flow.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")

    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=state_data,
        code_challenge_method=None,
    )
    
    # print('Generated auth_url:', auth_url)

    # Remove PKCE params
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
    parsed = urlparse(auth_url)
    # print('Parsed auth_url:', parsed)
    params = parse_qs(parsed.query, keep_blank_values=True)
    # print('Parsed query params before cleanup:', params)
    params.pop('code_challenge', None)
    params.pop('code_challenge_method', None)
    clean_params = {k: v[0] for k, v in params.items()}
    clean_url = urlunparse(parsed._replace(query=urlencode(clean_params)))

    return Response({"authorization_url": clean_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def gmail_callback(request):
    """Step 2 — Exchange code for tokens and redirect back to playbook page."""
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

    # Handle errors
    if not code:
        return redirect(f"{frontend_url}?error=no_code")
    
    if not state:
        return redirect(f"{frontend_url}?error=no_state")

    # ✅ Decode BOTH user_id AND agent_id from state
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        user_id = state_data.get("user_id")
        agent_id = state_data.get("agent_id")  # ✅ Extract agent_id
    except Exception as e:
        return redirect(f"{frontend_url}?error=invalid_state")

    if not user_id:
        return redirect(f"{frontend_url}?error=no_user_id")

    # Get user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect(f"{frontend_url}?error=user_not_found")

    # Exchange code for tokens
    try:
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
            error_msg = token_data.get('error_description', 'token_exchange_failed')
            return redirect(f"{frontend_url}?error={error_msg}")

        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token', '')

    except Exception as e:
        return redirect(f"{frontend_url}?error=exception")

    # ✅ Save tokens to database
    Integration.objects.update_or_create(
        user=user,
        provider='gmail',
        defaults={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'is_active': True,
        }
    )
    
    register_gmail_watch(user)

    # ✅ Redirect back to the EXACT playbook page they came from
    if agent_id:
        return redirect(f"{frontend_url}/playbooks/{agent_id}?oauth=success")
    else:
        return redirect(f"{frontend_url}/workflows?oauth=success")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gmail_watch(request):
    """Register Gmail push notifications."""
    try:
        result = register_gmail_watch(request.user)
        return Response({
            "message": "Gmail watch registered successfully.",
            "expiration": result.get('expiration'),
            "historyId": result.get('historyId'),
        })
    except Exception as e:
        return Response({"error": str(e)}, status=400)