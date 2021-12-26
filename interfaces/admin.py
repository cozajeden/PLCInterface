from django.contrib import admin
from .models import Interface, Order, Status

# Register your models here.
admin.site.register(Interface)
admin.site.register(Order)
admin.site.register(Status)