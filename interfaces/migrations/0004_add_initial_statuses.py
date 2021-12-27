# Generated by Django 4.0 on 2021-12-27 18:08

from django.db import migrations


def create_initial_interface(apps, schema_editor):
    Status = apps.get_model('interfaces', 'Status')
    for status in ['requested', 'finished', 'stopped']:
        Status.objects.create(status=status)


class Migration(migrations.Migration):

    dependencies = [
        ('interfaces', '0003_add_initial_commands'),
    ]

    operations = [
    ]
