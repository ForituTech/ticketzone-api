# Generated by Django 4.0.2 on 2022-02-05 22:34

import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_alter_event_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="created_at",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="event",
            name="updated_at",
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name="eventpromotion",
            name="created_at",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="eventpromotion",
            name="updated_at",
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name="ticketpromotion",
            name="created_at",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ticketpromotion",
            name="updated_at",
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name="tickettype",
            name="created_at",
            field=models.DateField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tickettype",
            name="updated_at",
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="eventpromotion",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="ticketpromotion",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="tickettype",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
            ),
        ),
    ]
