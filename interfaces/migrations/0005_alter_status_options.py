# Generated by Django 3.2.7 on 2021-12-26 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interfaces', '0004_alter_status_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'verbose_name_plural': 'Statuses'},
        ),
    ]
