from django.urls import path
from . import views

urlpatterns = [
    path('', views.gmail_pubsub_webhook, name='gmail-pubsub-webhook'),
]