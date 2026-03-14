from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    ProfileView, ChangePasswordView,
    ForgotPasswordView, ResetPasswordView,
    GoogleLoginView, EnableMFAView,
    VerifyMFALoginView,VerifyMFASetupView
)
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', RegisterView.as_view(),name="register"),
    path('login/', LoginView.as_view(),name="login"),
    path('logout/', LogoutView.as_view(),name="logout"),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('me/', ProfileView.as_view(),name="profile"),
    path('change-password/', ChangePasswordView.as_view(),name="change-password"),

    path('forgot-password/', ForgotPasswordView.as_view(),name="forgot-password"),
    path('reset-password/', ResetPasswordView.as_view(),name="reset-password"),
    
    path("auth/google/", GoogleLoginView.as_view(),name="google-login"),
    
    path("mfa/enable/", EnableMFAView.as_view(),name="enable-mfa"),
    path("mfa/setup/verify/", VerifyMFASetupView.as_view(),name="verify-mfa-setup"),
    path("mfa/login/verify/", VerifyMFALoginView.as_view(),name="verify-mfa-login"),
]

