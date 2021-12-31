from django.db import models

from django.conf import settings
from django.db import models
from django.db.models import Q


class Interface(models.Model):
    """
    Name of the operator GUI and coresponding PLC address
    """
    name = models.CharField(max_length=255)
    plc_address = models.CharField(max_length=100)
    plc_port = models.IntegerField()

    def __str__(self):
        return f'{self.name} - {self.plc_address}:{self.plc_port}'


class Status(models.Model):
    """
    Status of the order
    """
    status = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name_plural = 'Statuses'


class OrderManager(models.Manager):
    """
    Manager for Order model
    """

    def place_order(self, interface_name: str, order_number: int, requested_amount: int):
        """
        Place order in the database
        """
        requested_orders =  super().get_queryset().filter(
            Q(status__status=Status.objects.get(status='requested')) &
            Q(interface=Interface.objects.get(name=interface_name))
        )
        for order in requested_orders:
            order.status = Status.objects.get(status='stopped')
            order.save()
        order, created = super().update_or_create(
            interface=Interface.objects.get(name=interface_name),
            number=order_number,
            defaults = {
                'status': Status.objects.get(status='requested'),
                'requested_amount': requested_amount
            }
        )
        if not created and order.completed_amount >= requested_amount:
            order.status = Status.objects.get(status='finished')
            order.save()
            return order, False
        return order, True

    def update_order(self, interface_name: str, number: int, remaining_amount: int):
        """
        Update order in the database
        """
        interface = Interface.objects.get(name=interface_name)
        try:
            order = self.get(
                interface=interface,
                number=number
            )
        except Order.DoesNotExist:
            return False

        # Update completed amount only if order is not finished
        if order.requested_amount >= order.completed_amount:
            order.completed_amount = order.requested_amount - remaining_amount

        if order.completed_amount >= order.requested_amount:
            order.status = Status.objects.get(status='finished')
        order.save()
        return order


class Order(models.Model):
    """
    Prodiction order
    """
    number = models.IntegerField()
    requested_amount = models.IntegerField()
    completed_amount = models.IntegerField(default=0)
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    def __str__(self):
        return f'Order {self.number}, requested {self.requested_amount}, completed {self.completed_amount}, status {self.status}'


class CommandManager(models.Manager):
    """
    Manager for Command model
    """
    def get_command_as_bytes(self, interface: str, command: str) -> bytearray:
        """
        Get command as bytes
        """
        interface = Interface.objects.get(name=interface)
        command = self.get(interface=interface, command=command)
        fields = [
            'protocol_id', 'length', 'unit_id', 'function', 'starting_address', 'data'
        ]
        data = ''.join([command.__getattribute__(field) for field in fields])
        return bytearray.fromhex(data)


class Command(models.Model):
    """
    Predefinied command to be sent to the PLC
    """
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    command = models.CharField(max_length=255)
    protocol_id = models.CharField(default='0000', max_length=4)
    length = models.CharField(default='0006', max_length=4)
    unit_id = models.CharField(max_length=2)
    function = models.CharField(max_length=2)
    starting_address = models.CharField(max_length=4)
    data = models.CharField(max_length=255, null=True, blank=True)

    objects = CommandManager()

    class Meta:
        unique_together = ('interface', 'command')

    def __str__(self):
        return self.command
