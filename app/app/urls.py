from django.contrib import admin
from django.urls import path, include
from channels.routing import ProtocolTypeRouter, URLRouter
from api.routing import websocket_urlpatterns  # Import WebSocket URL patterns from api.routing


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns)
})
