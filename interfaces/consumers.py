import asyncio
import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Command


class PLCInterfaceConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("received", event)
        data = json.loads(event['text'])
        if data['button'] == 'Start':
            print(await self.start_PLC(
                self.scope['url_route']['kwargs']['interface_name']
            ))

    async def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def start_PLC(self, interface_name):
        return Command.objects.get_command_as_bytes(interface_name, 'start')