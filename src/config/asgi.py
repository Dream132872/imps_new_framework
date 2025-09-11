"""
ASGI config for conf project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from typing import Any
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


async def lifespan(scope: Any, receive: Any, send: Any):
    """Handle lifespan events (startup/shutdown)."""
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                # Add any startup logic here
                # For example: initialize database connections, caches, etc.
                print("ASGI application starting up...")
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                # Add any shutdown logic here
                # For example: close database connections, cleanup resources
                print("ASGI application shutting down...")
                await send({"type": "lifespan.shutdown.complete"})
                break


routes = []

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routes))
        ),
        "lifespan": lifespan,
    }
)
