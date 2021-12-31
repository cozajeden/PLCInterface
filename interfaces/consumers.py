import asyncio
import json
from typing import List, Optional, Tuple, Union
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
    Compose status response to the client
    """
    return {
                "type": "websocket.send",
                "text": json.dumps({
                    "type": "status",
                    "status": status,
                    "order": order,
                    "amount": amount,
                })
            }

def compose_update_table_message(
    mmessages: List[str],
) -> dict:
    """
    Compose table update response to the client
    """
    chunk_len = [4, 4, 4, 2, 2]
    rows = []
    for pair in mmessages:
        for type, msg in zip(['sent', 'received'], pair):
            table_fields = [type]
            for i in chunk_len:
                table_fields.append(msg[:i])
                msg = msg[i:]
            table_fields.append(msg)
            rows.append(table_fields)
    return {
                "type": "websocket.send",
                "text": json.dumps({
                    "type": "update_table",
                    "table_fields": rows
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

        connected = await self.connect_to_PLC()

        await self.send(compose_response_message("Połączono"))

    async def websocket_receive(self, event):
        """
        Method for processing websocket message.
        """
        # try to reconnect to PLC
        if not self.plc.connected:
            await self.connect_to_PLC()

        # process data
        data = json.loads(event['text'])
        if data['requested_amount']:
            data['requested_amount'] = int(data['requested_amount'])
        else:
            data['requested_amount'] = 0
        if data['number']:
            data['number'] = int(data['number'])
        else:
            data['number'] = 0

        # process client request
        if data['button'] == 'Start':
            await self.process_start_request(data)
        elif data['button'] == 'Stop':
            await self.process_stop_request()
        elif data['button'] == 'update':
            await self.process_update_request()

    async def process_stop_request(self) -> None:
        """
        Method for processing stop request.
        """
        order, success, messages = await self.stop_PLC(
            self.scope['url_route']['kwargs']['interface_name']
        )
        if not success or not order:
            await self.send(compose_response_message())
        else:
            await self.send(
                compose_response_message(
                    "Stop",
                    order.number,
                    order.requested_amount - order.completed_amount)
                )
            await self.send(compose_update_table_message(messages))

    async def process_start_request(self, data:dict) -> None:
        """
        Method for processing start request.
        """
        if data['requested_amount'] <= 0:
            return

        order, success, messages = await self.start_PLC(
            self.scope['url_route']['kwargs']['interface_name'],
            data['number'],
            data['requested_amount']
        )

        if not success:
            await self.send(compose_response_message())
        else:
            await self.send(
                compose_response_message(
                    "Start",
                    order.number,
                    order.requested_amount - order.completed_amount
                    )
            )
            await self.send(compose_update_table_message(messages))

    async def process_update_request(self) -> None:
        """
        Method for processing update request.
        """
        order, status, success, messages = await self.fetch_data_from_PLC(
            self.scope['url_route']['kwargs']['interface_name']
        )

        if not success:
            await self.send(compose_response_message())
        else:
            if order:
                await self.send(
                    compose_response_message(
                        "Start" if status else "Stop",
                        order.number,
                        order.requested_amount - order.completed_amount)
                )
            else:
                await self.send(
                    compose_response_message("Start" if status else "Stop")
                )
            await self.send(compose_update_table_message(messages))


    async def websocket_disconnect(self, event) -> None:
        """
        Method for processing websocket disconnection.
        """
        print("disconnected", event)
        if self.plc.connected:
            self.plc.disconnect()

    async def connect_to_PLC(self) -> bool:
        """
        Method for connecting to PLC
        """
        interface = await self.get_interface(self.scope['url_route']['kwargs']['interface_name'])
        self.plc = PLCController(
            interface.name,
            interface.plc_address,
            interface.plc_port
        )
        return self.plc.connect()

    @database_sync_to_async
    def get_interface(self, interface_name: str) -> Interface:
        """
        Get interface by name
        """
        return Interface.objects.get(name=interface_name)

    @database_sync_to_async
    def start_PLC(
        self, interface_name:str, order_number:int, requested_amount:int
    ) -> Tuple[Union[Order, bool], bool, Union[List[Tuple[str, str]], bool]]:
        """
        Place order and start PLC
        """
        messages = []

        # place order
        order, valid = Order.objects.place_order(interface_name, order_number, requested_amount)
        if not valid:
            return order, False, False

        # Write remaining amount to PLC
        remains = requested_amount - order.completed_amount
        success, value, msg, recv = self.plc.write_amount_to_PLC(interface_name, remains)
        if not success:
            return order, False, False
        messages.append((msg, recv))

        # Write order number to PLC
        success, value, msg, recv = self.plc.write_order_to_PLC(interface_name, order_number)
        if not success:
            return order, False, False
        messages.append((msg, recv))

        # Start PLC
        success, value, msg, recv = self.plc.write_status_to_PLC(interface_name, True)
        if not success:
            return order, False, False
        messages.append((msg, recv))

        return order, True, messages

    @database_sync_to_async
    def stop_PLC(
        self, interface_name:str
    ) -> Tuple[Union[Order, bool], bool, Union[List[Tuple[str, str]], bool]]:
        """
        Stop PLC
        """
        messages = []

        # Stop PLC
        success, value, msg, recv = self.plc.write_status_to_PLC(interface_name, False)
        if not success:
            return False, False, False
        messages.append((msg, recv))
        
        # read order number from PLC
        success, order_number, msg, recv = self.plc.read_order_from_PLC(interface_name)
        if not success:
            return False, False, False
        messages.append((msg, recv))

        # read remaining amount from PLC
        success, amount, msg, recv = self.plc.read_amount_from_PLC(interface_name)
        if not success:
            return False, False, False
        messages.append((msg, recv))
        
        # update order in database
        order = Order.objects.update_order(interface_name, order_number, amount)
        return order, True, messages

    @database_sync_to_async
    def fetch_data_from_PLC(
        self, interface_name:str
    ) -> Tuple[Union[Order, bool], bool, bool, Union[List[Tuple[str, str]], bool]]:
        """
        Fetch data from PLC and update order in database
        """
        messages = []

        # read remaining amount from PLC
        success, amount, msg, recv = self.plc.read_amount_from_PLC(interface_name)
        if not success:
            return False, False, False, False
        messages.append((msg, recv))

        # read order number from PLC
        success, order_number, msg, recv = self.plc.read_order_from_PLC(interface_name)
        if not success:
            return False, False, False, False
        messages.append((msg, recv))
        
        # read running status from PLC
        success, status, msg, recv = self.plc.read_status_from_PLC(interface_name)
        if not success:
            return False, False, False, False
        messages.append((msg, recv))

        # update order in database
        order = Order.objects.update_order(interface_name, order_number, amount)
        return order, status, True, messages