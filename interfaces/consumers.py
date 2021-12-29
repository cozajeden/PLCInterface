import asyncio
import json
from typing import Optional, Union
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Command, Order, Interface, Status
from .views import NO_CONNECTED_PLC_ERROR
from .PLCController import PLCController

def compose_response_message(
    status: str = NO_CONNECTED_PLC_ERROR,
    order: int = 0,
    amount: int = 0,
) -> dict:
    """
    Compose response to the client
    """
    return {
                "type": "websocket.send",
                "text": json.dumps({
                    "type": "ststus",
                    "status": status,
                    "order": order,
                    "amount": amount,
                })
            }


class PLCInterfaceConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        """
        Method for processing websocket connection,
        and initializing PLC connection.
        """
        print("connected", event)
        await self.send({
            "type": "websocket.accept"
        })

        interface = await self.get_interface(self.scope['url_route']['kwargs']['interface_name'])
        self.plc = PLCController(
            interface.name,
            interface.plc_address,
            interface.plc_port
        )
        connected = self.plc.connect()

        # If PLCController is not connected, close websocket connection
        if not connected:
            self.disconnect()
            return

        await self.send(compose_response_message("Połączono"))

    async def websocket_receive(self, event):
        """
        Method for processing websocket message.
        """
        print("received", event)
        data = json.loads(event['text'])

        # Start request
        if data['button'] == 'Start' and data['amount'] > 0:
            order = await self.start_PLC(
                self.scope['url_route']['kwargs']['interface_name'],
                data['number'],
                data['amount']
            )
            if not order:
                self.disconnect()
            else:
                self.send(
                    compose_response_message("Start", order.order_number, order.complete_amount)
                )
            return

        # Stop request
        if data['button'] == 'Stop':
            order = await self.stop_PLC(
                self.scope['url_route']['kwargs']['interface_name']
            )
            if not order:
                self.disconnect()
            else:
                self.send(
                    compose_response_message("Stop", order.order_number, order.completed_amount)
                    )
            return

        # Update request
        if data['button'] == 'Update':
            order, running = await self.fetch_data_from_PLC(
                self.scope['url_route']['kwargs']['interface_name']
            )
            if not order:
                self.disconnect()
            else:
                self.send(
                    compose_response_message(
                        "Start" if running else "Stop",
                        order.number,
                        order.completed_amount)
                )
            return
            


    async def websocket_disconnect(self, event):
        """
        Method for processing websocket disconnection.
        """
        print("disconnected", event)
        if self.plc.connected:
            self.plc.disconnect()

    async def disconnect(self, event):
        """
        Method for processing disconnection.
        """
        await self.send(compose_response_message())
        await self.send({
            "type": "websocket.close",
        })

    @database_sync_to_async
    def get_interface(self, interface_name: str) -> Interface:
        """
        Get interface by name
        """
        return Interface.objects.get(name=interface_name)

    @database_sync_to_async
    def start_PLC(self, interface_name:str, order_number:int, requested_amount:int) -> Union[Order, bool]:
        """
        Place order and start PLC
        """
        order, valid = Order.objects.place_order(interface_name, order_number, requested_amount)
        if not valid:
            return False

        command = Command.objects.get(interface_name, 'write_amount')
        hi_amount = int(requested_amount / 255)
        lo_amount = requested_amount % 255
        command.append(hi_amount)
        command.append(lo_amount)
        success = self.plc.send(command)
        if not success:
            return False

        command = Command.objects.get_command_as_bytes(interface_name, 'start')
        success = self.plc.send(command)
        if not success:
            return False

        return order

    @database_sync_to_async
    def stop_PLC(self, interface_name:str):
        """
        Stop PLC
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'stop')
        success = self.plc.send(command)
        if not success:
            return False

        order = Order.objects.cancel_order(interface_name)
        return order

    @database_sync_to_async
    def fetch_data_from_PLC(self, interface_name:str):
        """
        Fetch data from PLC and update order in database
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'read_amount')
        amount = self.plc.send(command)
        if not amount:
            return False, False
        amount = int(amount, 16)

        command = Command.objects.get_command_as_bytes(interface_name, 'read_status')
        running = self.plc.send(command)
        if not running:
            return False, False
        running = bool(int(running, 16))

        order = Order.objects.update_order(interface_name, amount)
        return order, running