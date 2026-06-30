from django.urls import path
from . import views

urlpatterns = [
    path("", views.NewGmailPubSubWebhookView.as_view(), name="gmail-pubsub-webhook"),
]
