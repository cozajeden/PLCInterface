from django.test import TestCase
from interfaces.PLCController import PLCController
import dummyPLC
import threading
import time

class PLCControllerTestCase(TestCase):
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
        success, order_number, msg, recv = self.plc.read_order_from_PLC('interface1')
        self.assertTrue(success)
        self.assertEqual(order_number, 0)
        self.assertEqual(recv, '0001000000050103020000')

    def test_can_send_read_amount_command(self):
        success, amount, msg, recv = self.plc.read_amount_from_PLC('interface1')
        self.assertTrue(success)
        self.assertEqual(amount, 0)
        self.assertEqual(recv, '0001000000050103020000')

    def test_can_send_read_status_command(self):
        success, status, msg, recv = self.plc.read_status_from_PLC('interface1')
        self.assertTrue(success)
        self.assertEqual(status, 0)
        self.assertEqual(recv, '00010000000401010100')

    def test_can_send_write_read_amount_command(self):
        success, value, msg, recv = self.plc.write_amount_to_PLC('interface1', 25)
        self.assertTrue(success)
        self.assertEqual(recv, '000100000006011000000001')

        success, amount, msg, recv = self.plc.read_amount_from_PLC('interface1')
        self.assertTrue(success)
        self.assertEqual(amount, 25)
        self.assertEqual(recv, '0002000000050103020019')

    def test_can_send_write_read_order_command(self):
        success, value, msg, recv = self.plc.write_order_to_PLC('interface1',24)
        self.assertTrue(success)
        self.assertEqual(recv, '000100000006011000ff0001')

        success, order_number, msg, recv = self.plc.read_order_from_PLC('interface1')
        self.assertTrue(success)
        self.assertEqual(order_number, 24)
        self.assertEqual(recv, '0002000000050103020018')

    def test_can_send_start_stop_command(self):
        success, value, msg, recv = self.plc.write_status_to_PLC('interface1', True)
        self.assertTrue(success)
        self.assertEqual(recv, '00010000000601050010ff00')

        success, value, msg, recv = self.plc.write_status_to_PLC('interface1', False)
        self.assertTrue(success)
        self.assertEqual(recv, '000200000006010500100000')