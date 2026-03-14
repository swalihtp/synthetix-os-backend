from django.urls import path
from . import views

urlpatterns = [
    path('webhook/<str:path>/', views.webhook_trigger, name='webhook-trigger'),
    path('api/<str:agent_id>/', views.api_trigger, name='api-trigger'),
    path('gmail/', views.gmail_webhook, name='gmail-webhook'),
]