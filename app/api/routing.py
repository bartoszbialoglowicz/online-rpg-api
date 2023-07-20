from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from api import consumers

websocket_urlpatterns = [
    path('ws/combat/', consumers.CombatSystemConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns)
})