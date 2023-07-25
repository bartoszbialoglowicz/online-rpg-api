from django.urls import re_path
from api import consumers

websocket_urlpatterns = [
    re_path(r'ws/combat/', consumers.CombatSystemConsumer.as_asgi()),
]
