print("👉 ASGI entrypoint is live")
import os
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import PrimatesGameAPI.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PrimatesGame.settings')

application = ProtocolTypeRouter({
    # HTTP goes to Django as usual:
    "http": get_asgi_application(),

    # WebSocket connections go through Channels:
    "websocket": AuthMiddlewareStack(
        URLRouter(
            PrimatesGameAPI.routing.websocket_urlpatterns
        )
    ),
})