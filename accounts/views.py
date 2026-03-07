from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from accounts.serializers.register_serializer import RegisterSerializer
from accounts.serializers.login_serializer import LoginSerializer
from accounts.serializers.user_serializer import UserSerializer
from accounts.serializers.changepassword_serializer import ChangePasswordSerializer
from accounts.serializers.forgotpassword_serializer import ForgotPasswordSerializer
from accounts.serializers.resetpassword_serializer import ResetPasswordSerializer
from.services.auth_service import AuthService
from .permissions.rbac_permission import RBACPermission

from accounts.utils.password_reset_token import password_reset_token
from .services.email_service import EmailService
from .services.google_auth_service import GoogleAuthService

User = get_user_model()

# REGISTER
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.register_user(serializer.validated_data)

        return Response({"message": "User created"}, status=201)

# LOGIN
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        tokens = AuthService.login_user(user)

        return Response(tokens)

# LOGOUT
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out"})
        except Exception:
            return Response(status=400)

# PROFILE
class ProfileView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    required_permission = "view_profile"

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# CHANGE PASSWORD
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.check_password(serializer.data['old_password']):
            return Response({"error": "Wrong password"}, status=400)

        request.user.set_password(serializer.data['new_password'])
        request.user.save()

        return Response({"message": "Password updated"})

# FORGOT PASSWORD
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.data['email'])
        except User.DoesNotExist:
            return Response({"message": "If email exists, link sent"})

        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = password_reset_token.make_token(user)

        # Send email (you must configure email backend)
        print(f"Reset link: /reset-password/{uid}/{token}")
        EmailService.send_password_reset_email('http://localhost:5173/reset-password/',uid,token,request.user)

        return Response({"message": "Reset link sent to your registered email address"})
    
# RESET PASSWORD
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = serializer.data['token']
            uid = serializer.data['uid']
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)

        if not password_reset_token.check_token(user, token):
            return Response({"error": "Token expired"}, status=400)

        user.set_password(serializer.data['new_password'])
        user.save()

        return Response({"message": "Password reset successful"})
    
#  Google Oauth
class GoogleLoginView(APIView):

    def post(self, request):

        token = request.data.get("token")

        google_user = GoogleAuthService.verify_google_token(token)

        if not google_user:
            return Response({"error": "Invalid token"}, status=400)

        email = google_user["email"]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": google_user["name"]
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "fullname": user.full_name
            }
        })