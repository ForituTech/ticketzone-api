# Generated by Django 4.0.3 on 2022-03-20 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0002_payment_reconciled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="made_through",
            field=models.CharField(default="MPESA", max_length=255),
        ),
    ]
