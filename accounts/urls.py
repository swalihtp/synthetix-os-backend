from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    ProfileView, ChangePasswordView,
    ForgotPasswordView, ResetPasswordView,
    GoogleLoginView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),

    path('me/', ProfileView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),

    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    
    path("auth/google/", GoogleLoginView.as_view())
]