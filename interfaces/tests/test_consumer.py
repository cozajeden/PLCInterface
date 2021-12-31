from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from interfaces.consumers import compose_response_message, compose_update_table_message
from interfaces.consumers import PLCInterfaceConsumer
import json
import asyncio

class MessagesComposeTestCase(TestCase):
    def test_can_compose_default_response_message(self):
        message = compose_response_message()
        self.assertEqual(message, {
            "type": "websocket.send",
            "text": json.dumps({
                "type": "status",
                "status": "Brak połączenia z PLC",
                "order": 0,
                "amount": 0,
            })
        })

    def test_can_compose_response_message(self):
        message = compose_response_message('test', 5, 8)
        self.assertEqual(message, {
            "type": "websocket.send",
            "text": json.dumps({
                "type": "status",
                "status": "test",
                "order": 5,
                "amount": 8,
            })
        })

    def test_can_compose_update_table_message(self):
        message = compose_update_table_message(
            [('0000000601050010ff00', '0000000601050010ff00')]
        )
        self.assertEqual(message, {
            "type": "websocket.send",
            "text": json.dumps({
                "type": "update_table",
                "table_fields": [
                    ["sent", "0000", "0006", "0105", "00", "10", "ff00"],
                    ["received", "0000", "0006", "0105", "00", "10", "ff00"]
                ],
            })
        })


class PLCInterfaceConsumerTestCase(TestCase):
    def get_communicator(self, interface_path='interfaces/interface1/') -> WebsocketCommunicator:

        app = URLRouter([
            path('interfaces/<str:interface_name>/', PLCInterfaceConsumer()),
        ])
        communicator = WebsocketCommunicator(app, interface_path)
        return communicator

    async def test_can_connect(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_can_receive_message(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"uV06k70dXJRGAIkQy86p8NC7KfmuXjXnASXyJyoonH5xY001mG0bF6q6BGZRR2bJ",
                "number":"",
                "requested_amount":"",
                "button":"Start"
        })

        await communicator.disconnect()

    async def can_return_status_message_after_update_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"uV06k70dXJRGAIkQy86p8NC7KfmuXjXnASXyJyoonH5xY001mG0bF6q6BGZRR2bJ",
                "number":"",
                "requested_amount":"",
                "button":"update"
        })

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"uV06k70dXJRGAIkQy86p8NC7KfmuXjXnASXyJyoonH5xY001mG0bF6q6BGZRR2bJ",
                "number":"",
                "requested_amount":"",
                "button":"Update"
        })

        await communicator.disconnect()