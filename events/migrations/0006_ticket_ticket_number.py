# Generated by Django 4.0.4 on 2022-05-14 17:01

from distutils import core

from django.db import migrations, models

import core.utils


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0005_alter_event_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="ticket_number",
            field=models.CharField(
                default=core.utils.generate_ticket_number, max_length=255
            ),
        ),
    ]
