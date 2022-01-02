from django.test import TestCase
from interfaces.models import Status

class StatusTest(TestCase):
    def test_contains_default_commands(self):
        """
        Test if default commands are in Status model
        """
        statuses = ['requested', 'finished', 'stopped']
        for status in statuses:
            self.assertTrue(Status.objects.filter(status=status).exists())