# Generated by Django 4.0.3 on 2022-03-12 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0008_alter_event_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="time",
            field=models.TimeField(default="22:36"),
        ),
    ]
