# Generated by Django 4.1.1 on 2022-09-29 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0009_ticketscan"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketscan",
            name="redeem_triggered",
            field=models.BooleanField(default=False),
        ),
    ]
