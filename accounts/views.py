from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from accounts.serializers.verify_email_serializer import VerifyEmailSerializer
from .services.auth_service import AuthService
from accounts.utils.password_reset_token import password_reset_token
from .services.email_service import EmailService
from .services.google_auth_service import GoogleAuthService
from .services.mfa_service import MFAService
from .models import EmailVerification
from .utils.otp_geneation import generate_otp, hash_otp, get_expiry
from .throttles import (
    LoginThrottle,
    RegisterThrottle,
    ForgotPasswordThrottle,
    ResetPasswordThrottle,
    VerifyEmailThrottle,
    ResendOTPThrottle,
    GoogleLoginThrottle,
    ProfileThrottle,
    ChangePasswordThrottle,
    MFAThrottle,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.register_user(serializer.validated_data)
        return Response(
            {
                "message": "Registration successful. Please check your email for the verification code. If you not found also check your spam"
            },
            status=201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        if user.mfa_enabled:
            return Response({"mfa_required": True, "user_id": user.id})
        tokens = AuthService.login_user(user)
        return Response(tokens)


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


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ProfileThrottle]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChangePasswordThrottle]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.data["old_password"]):
            return Response({"error": "Wrong password"}, status=400)
        request.user.set_password(serializer.data["new_password"])
        request.user.save()
        return Response({"message": "Password updated"})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data["email"])
        except User.DoesNotExist:
            return Response({"message": "If email exists, link sent"})
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = password_reset_token.make_token(user)
        print(f"Reset link: /reset-password/{uid}/{token}")
        EmailService.send_password_reset_email(
            "http://localhost:5173", uid, token, user
        )
        return Response({"message": "Reset link sent to your registered email address"})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ResetPasswordThrottle]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = serializer.data["token"]
            uid = serializer.data["uid"]
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except Exception:
            return Response({"error": "Invalid token"}, status=400)
        if not password_reset_token.check_token(user, token):
            return Response({"error": "Token expired"}, status=400)
        user.set_password(serializer.data["new_password"])
        user.save()
        return Response({"message": "Password reset successful"})


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [GoogleLoginThrottle]

    def post(self, request):
        token = request.data.get("token")
        google_user = GoogleAuthService.verify_google_token(token)
        if not google_user:
            return Response({"error": "Invalid token"}, status=400)
        email = google_user["email"]
        user, created = User.objects.get_or_create(
            email=email, defaults={"full_name": google_user["name"]}
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"email": user.email, "fullname": user.full_name},
            }
        )


class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [MFAThrottle]

    def post(self, request):
        user = request.user
        if not user.mfa_secret:
            user.mfa_secret = MFAService.generate_secret()
            user.save()
        uri = MFAService.get_qr_uri(user)
        return Response({"qr_uri": uri})


class VerifyMFASetupView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [MFAThrottle]

    def post(self, request):
        otp = request.data.get("otp")
        if MFAService.verify_otp(request.user, otp):
            request.user.mfa_enabled = True
            request.user.save()
            return Response({"message": "MFA enabled successfully"})
        return Response({"error": "Invalid OTP"}, status=400)


class VerifyMFALoginView(APIView):
    throttle_classes = [LoginThrottle]
    permission_classes = [AllowAny]  

    def post(self, request):
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        if not MFAService.verify_otp(user, otp):
            return Response({"error": "Invalid OTP"}, status=400)
        tokens = AuthService.login_user(user)
        return Response(tokens)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [VerifyEmailThrottle]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        user.email_verification.delete()
        return Response({"message": "Email verified successfully"})


class ResendVerificationOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ResendOTPThrottle]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)
        if user.is_verified:
            return Response({"detail": "Email already verified"}, status=400)
        otp = generate_otp()
        EmailVerification.objects.update_or_create(
            user=user, defaults={"otp": hash_otp(otp), "expires_at": get_expiry()}
        )
        EmailService.send_verification_email(user=user, otp=otp)
        return Response({"message": "Verification code sent"})
