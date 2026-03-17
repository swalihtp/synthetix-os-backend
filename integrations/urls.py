from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, gmail_connect, gmail_callback,gmail_watch, calendar_connect, calendar_callback 


router = DefaultRouter()
router.register(r'', IntegrationViewSet, basename='integration')

urlpatterns = [
    path('gmail/connect/', gmail_connect, name='gmail-connect'),
    path('gmail/callback/', gmail_callback, name='gmail-callback'),
    path('calendar/connect/', calendar_connect, name='calendar-connect'),
    path('calendar/callback/', calendar_callback, name='calendar-callback'),
    path('gmail/watch/', gmail_watch, name='gmail-watch'),

    path('', include(router.urls)),
]
