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


# class Command:
#     """Command to be sent to the PLC"""
#     order = models.ForeignKey(Order, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)