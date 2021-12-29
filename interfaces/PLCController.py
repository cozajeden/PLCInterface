import socket
from itertools import cycle

class PLCController:
    def __init__(self, interface_name: str, plc_address: str, plc_port: int):
        self.interface_name = interface_name
        self.plc_address = plc_address
        self.plc_port = plc_port
        self.connected = False
        self.connection = None
        self.loop = None
        self.reader = None
        self.writer = None
        self.cyclic_transaction_id = cycle([f'{i:04x}' for i in range(1, 65535)])


    def connect(self):
        return False

    def disconnect(self):
        return False

    def send(self, command: bytes):
        return False

    def receive(self):
        return False
