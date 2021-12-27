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


class Status(models.Model):
    """
    Status of the order
    """
    status = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Statuses'


class Order(models.Model):
    """
    Prodiction order
    """
    number = models.IntegerField()
    requested_amount = models.IntegerField()
    completed_amount = models.IntegerField()
    interface = models.ForeignKey(Interface, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
