# Generated by Django 4.0.4 on 2022-05-14 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_event_event_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="eventcategory",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="eventpromotion",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="reminderoptin",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="ticket",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="ticketpromotion",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="tickettype",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
