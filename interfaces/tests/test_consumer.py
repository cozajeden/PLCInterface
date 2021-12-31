from django.test import TestCase
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import path
from interfaces.consumers import compose_response_message, compose_update_table_message
from interfaces.consumers import PLCInterfaceConsumer
from interfaces.PLCController import PLCController
import json
import asyncio
import threading
import time
import dummyPLC

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


class PLCInterfaceConsumerPLCDisonnectedTestCase(TestCase):
    """
    Test cases for PLCInterfaceConsumer when PLC is disconnected
    """
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
                "csrfmiddlewaretoken":"",
                "number":"",
                "requested_amount":"",
                "button":"Start"
        })

        await communicator.disconnect()

    async def test_can_return_messages_after_update_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"",
                "requested_amount":"",
                "button":"update"
        })

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Brak połączenia z PLC')

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Brak połączenia z PLC')

        await communicator.disconnect()

    async def test_can_return_messages_after_start_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"13",
                "requested_amount":"25",
                "button":"Start"
        })

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Brak połączenia z PLC')

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Brak połączenia z PLC')

        await communicator.disconnect()

    async def test_can_return_messages_after_stop_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"7",
                "requested_amount":"21",
                "button":"Start"
        })
        recieved_message = await communicator.receive_json_from()
        recieved_message = await communicator.receive_json_from()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"",
                "requested_amount":"",
                "button":"Stop"
        })

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Brak połączenia z PLC')

        await communicator.disconnect()


class PLCInterfaceConsumerPLCConnectedTestCase(TestCase):
    """
    Test cases for PLCInterfaceConsumer when PLC is connected
    """
    def get_communicator(self, interface_path='interfaces/interface1/') -> WebsocketCommunicator:

        app = URLRouter([
            path('interfaces/<str:interface_name>/', PLCInterfaceConsumer()),
        ])
        communicator = WebsocketCommunicator(app, interface_path)
        return communicator

    def setUp(self):
        self.dummmy_plc_stop_event = threading.Event()
        dummy_plc_started = threading.Event()
        self.server_thread = threading.Thread(
            target=dummyPLC.test_server,
            args=(True, self.dummmy_plc_stop_event, dummy_plc_started),
            daemon=True
        ).start()
        dummy_plc_started.wait()
        self.plc = PLCController('test', '127.0.1.101', 1024)
        self.plc.connect()
        
    def tearDown(self):
        self.dummmy_plc_stop_event.set()
        self.plc.disconnect()
        time.sleep(2)

    async def test_can_connect(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_can_receive_message(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"",
                "requested_amount":"",
                "button":"Start"
        })

        await communicator.disconnect()

    async def test_can_return_messages_after_update_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"",
                "requested_amount":"",
                "button":"update"
        })

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Połączono')

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Stop')

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'update_table')
        self.assertIn('table_fields', recieved_message)

        await communicator.disconnect()

    async def test_can_return_messages_after_start_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"13",
                "requested_amount":"25",
                "button":"Start"
        })

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Połączono')

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Start')
        self.assertEqual(recieved_message.get('order'), 13)
        self.assertEqual(recieved_message.get('amount'), 25)

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'update_table')
        self.assertIn('table_fields', recieved_message)

        await communicator.disconnect()

    async def test_can_return_messages_after_stop_request(self):
        communicator = self.get_communicator()
        connected, subprotocol = await communicator.connect()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"7",
                "requested_amount":"21",
                "button":"Start"
        })
        recieved_message = await communicator.receive_json_from()
        recieved_message = await communicator.receive_json_from()
        recieved_message = await communicator.receive_json_from()

        await communicator.send_json_to({
                "csrfmiddlewaretoken":"",
                "number":"",
                "requested_amount":"",
                "button":"Stop"
        })

        recieved_message = await communicator.receive_json_from()
        self.assertIn('type', recieved_message)
        self.assertEqual(recieved_message.get('type'), 'status')
        self.assertEqual(recieved_message.get('status'), 'Stop')
        self.assertEqual(recieved_message.get('order'), 7)
        self.assertEqual(recieved_message.get('amount'), 21)

        recieved_message = await communicator.receive_json_from()
        self.assertEqual(recieved_message.get('type'), 'update_table')
        self.assertIn('table_fields', recieved_message)

        await communicator.disconnect()