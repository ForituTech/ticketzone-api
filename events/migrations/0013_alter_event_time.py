# Generated by Django 4.0.3 on 2022-03-13 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0012_alter_event_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="time",
            field=models.TimeField(auto_now_add=True),
        ),
    ]