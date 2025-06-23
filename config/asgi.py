"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter

from apps.chat.middleware import JWTAuthMiddleware
from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # HTTP 요청 처리
        "websocket": JWTAuthMiddleware(  # WebSocket 요청 처리
            URLRouter(websocket_urlpatterns)
        ),
    }
)
