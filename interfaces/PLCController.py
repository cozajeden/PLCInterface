import socket
from itertools import cycle
from typing import Tuple, Union
from .models import Command

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
        self.connection = socket.socket()
        try:
            self.connection.connect((self.plc_address, self.plc_port))
            self.connected = True
            return True
        except socket.error:
            self.connected = False
            return False

    def disconnect(self):
        self.connection.close()
        self.connected = False

    def send(self, command: bytes) -> Tuple[bool, int, bytes, Union[bytes, None]]:
        transaction_id = next(self.cyclic_transaction_id)
        msg = bytearray.fromhex(transaction_id) + command
        mobus_function = msg[7]

        success = True
        value = 0
        recv = None
        
        try:
            self.connection.send(msg)
            recv = self.connection.recv(1024)
            if recv.hex()[:4] != transaction_id or recv[7] != mobus_function:
                success = False
            if mobus_function == 1: # read coils
                value = recv[-1]
            if mobus_function == 3: # read holding registers
                value = recv[-2] * 256 + recv[-1]
        except (socket.error, IndexError):
            try:
                self.disconnect()
            except socket.error:
                self.connected = False
            success = False
        
        msg = msg.hex()
        if recv is not None:
            recv = recv.hex()
        return success, value, msg, recv

    def write_amount_to_PLC(self, interface_name:str, amount: int) -> None:
        """
        Write amount to PLC
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'write_amount')
        hi_amount = int(amount / 256)
        lo_amount = amount % 256
        command.append(hi_amount)
        command.append(lo_amount)
        return self.send(command)

    def write_order_to_PLC(self, interface_name:str, order: int) -> None:
        """
        Write order to PLC
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'write_order')
        hi_order = int(order / 256)
        lo_order = order % 256
        command.append(hi_order)
        command.append(lo_order)
        return self.send(command)

    def write_status_to_PLC(self, interface_name:str, status: bool) -> None:
        """
        Write status to PLC
        """
        if status:
            command = Command.objects.get_command_as_bytes(interface_name, 'start')
        else:
            command = Command.objects.get_command_as_bytes(interface_name, 'stop')
        return self.send(command)

    def read_order_from_PLC(self, interface_name:str) -> int:
        """
        Read order from PLC
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'read_order')
        return self.send(command)

    def read_amount_from_PLC(self, interface_name:str) -> int:
        """
        Read amount from PLC
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'read_amount')
        return self.send(command)

    def read_status_from_PLC(self, interface_name:str) -> bool:
        """
        Read status from PLC
        """
        command = Command.objects.get_command_as_bytes(interface_name, 'read_status')
        return self.send(command)



if __name__ == '__main__':
    plc = PLCController('test', '127.0.1.101', 1024)
    plc.connect()
    ret = plc.send(bytearray.fromhex('00000006010100100001'))
    print(ret)