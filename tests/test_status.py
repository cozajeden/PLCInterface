from django.test import TestCase
from interfaces.models import Status

class StatusTest(TestCase):
    def test_contains_default_commands(self):
        statuses = ['requested', 'finished', 'stopped']
        for status in statuses:
            self.assertTrue(Status.objects.filter(status=status).exists())