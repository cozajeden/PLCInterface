from django.test import TestCase
from interfaces.models import Command

class CommandTest(TestCase):
    def test_contains_default_commands(self):
        """
        Test if all default commands are in Command model
        """
        commands = [
            'read_amount',
            'write_amount',
            'read_order',
            'write_order',
            'read_status',
            'start',
            'stop',
        ]
        for cmd in commands:
            self.assertTrue(Command.objects.filter(command=cmd).exists())

    def test_default_read_amount_command(self):
        """
        Test if default read_amount command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'read_amount')
        self.assertEqual(command, bytes.fromhex('00000006010300000001'))

    def test_default_write_amount_command(self):
        """
        Test if default write_amount command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'write_amount')
        self.assertEqual(command, bytes.fromhex('0000000901100000000102'))

    def test_default_read_order_command(self):
        """ 
        Test if default read_order command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'read_order')
        self.assertEqual(command, bytes.fromhex('00000006010300ff0001'))

    def test_default_write_order_command(self):
        """
        Test if default write_order command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'write_order')
        self.assertEqual(command, bytes.fromhex('00000009011000ff000102'))

    def test_default_read_status_command(self):
        """
        Test if default read_status command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'read_status')
        self.assertEqual(command, bytes.fromhex('00000006010100100001'))

    def test_default_start_command(self):
        """
        Test if default start command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'start')
        self.assertEqual(command, bytes.fromhex('0000000601050010ff00'))

    def test_default_stop_command(self):
        """
        Test if default stop command is correct
        """
        command = Command.objects.get_command_as_bytes('interface1', 'stop')
        self.assertEqual(command, bytes.fromhex('00000006010500100000'))