"""
ASGI config for channel project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

from interfaces.consumers import PLCInterfaceConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'channel.settings')

application = ProtocolTypeRouter({
    'wenbsocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('interfaces/<str:interface_name>/', PLCInterfaceConsumer),
                ]
            )
        )
    )
})
