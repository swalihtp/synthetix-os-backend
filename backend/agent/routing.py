from django.urls import re_path
from .consumers import AgentConsumer

websocket_urlpatterns = [
    re_path(r'ws/agents/(?P<agent_id>[0-9a-f-]+)/$', AgentConsumer.as_asgi()),
]