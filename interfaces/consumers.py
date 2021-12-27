import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async


class PLCInterfaceConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })
        interface_name = self.scope['url_route']['kwargs']['interface_name']
        print(self.scope['user'])
        await asyncio.sleep(10)
        await self.send({
            "type": "websocket.close",
        })

    async def websocket_receive(self, event):
        print("received", event)
        await self.send({
            "type": "websocket.send",
            "text": f"Hello {event['text']}!"
        })

    async def websocket_disconnect(self, event):
        print("disconnected", event)