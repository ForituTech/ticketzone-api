# Generated by Django 4.0.3 on 2022-04-15 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="uses",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="tickettype",
            name="use_limit",
            field=models.IntegerField(default=1),
        ),
    ]
