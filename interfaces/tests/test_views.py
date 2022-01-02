from django.test import TestCase
from django.urls import resolve
from interfaces.views import IndexView, InterfaceView

class InterfaceTest(TestCase):
    def test_index_url_resolves_to_index_view(self):
        """
        Test if index url resolves to index view
        """
        found = resolve('/interfaces/')
        self.assertEqual(found.func.__name__, IndexView.as_view().__name__)

    def test_interface_url_resolves_to_interface_view(self):
        """
        Test if interface url resolves to interface view
        """
        found = resolve('/interfaces/interface1/')
        self.assertEqual(found.func.__name__, InterfaceView.as_view().__name__)