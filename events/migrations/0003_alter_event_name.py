# Generated by Django 4.0.2 on 2022-02-04 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_event_partner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="name",
            field=models.CharField(default="new-event", max_length=256),
        ),
    ]
