from django.test import TestCase
from interfaces.PLCController import PLCController
import dummyPLC
import threading
import time

class PLCControllerTest(TestCase):
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

    def test_can_send_read_order_command(self):
        command = bytearray.fromhex('00000006010300ff0001')
        success, order_number, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(order_number, 0)
        self.assertEqual(recv, '0001000000050103020000')

    def test_can_send_read_amount_command(self):
        command = bytearray.fromhex('00000006010300000001')
        success, amount, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(amount, 0)
        self.assertEqual(recv, '0001000000050103020000')

    def test_can_send_read_status_command(self):
        command = bytearray.fromhex('00000006010100100001')
        success, status, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(status, 0)
        self.assertEqual(recv, '00010000000401010100')

    def test_can_send_write_read_amount_command(self):
        command = bytearray.fromhex('00000009011000000001020019')
        success, value, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(recv, '000100000006011000000001')

        command = bytearray.fromhex('00000006010300000001')
        success, amount, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(amount, 25)
        self.assertEqual(recv, '0002000000050103020019')

    def test_can_send_write_read_order_command(self):
        command = bytearray.fromhex('00000009011000ff0001020019')
        success, value, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(recv, '000100000006011000ff0001')

        command = bytearray.fromhex('00000006010300ff0001')
        success, order_number, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(order_number, 25)
        self.assertEqual(recv, '0002000000050103020019')

    def test_can_send_start_stop_command(self):
        command = bytearray.fromhex('0000000601050010ff00')
        success, value, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(recv, '00010000000601050010ff00')

        command = bytearray.fromhex('00000006010500100000')
        success, value, msg, recv = self.plc.send(command)
        self.assertTrue(success)
        self.assertEqual(recv, '000200000006010500100000')