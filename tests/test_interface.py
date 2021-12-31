from django.test import TestCase
from interfaces.models import Interface


class TestInterface(TestCase):
    def test_containing_default_interface(self):
        self.assertTrue(Interface.objects.filter(name='interface1').exists())