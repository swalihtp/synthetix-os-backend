from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, gmail_connect, gmail_callback,gmail_watch


router = DefaultRouter()
router.register(r'', IntegrationViewSet, basename='integration')

urlpatterns = [
    path('gmail/connect/', gmail_connect, name='gmail-connect'),
    path('gmail/callback/', gmail_callback, name='gmail-callback'),
    path('gmail/watch/', gmail_watch, name='gmail-watch'),

    path('', include(router.urls)),
]
