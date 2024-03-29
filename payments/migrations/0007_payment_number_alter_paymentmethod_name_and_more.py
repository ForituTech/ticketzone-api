# Generated by Django 4.1.2 on 2022-11-20 13:09
import uuid
from datetime import date
from typing import Any, Type

import django.db.models.deletion
from django.db import migrations, models

import core.utils


def generate_payment_number_(apps: Any, schema_editor: Any) -> None:
    from payments.models import Payment

    Payment_: Type[Payment] = apps.get_model("payments", "Payment")

    for payment in Payment_.objects.all():
        date_ = date.today()
        payment_number = (
            f"pmnt{date_.year}{date_.month}{date_.day}"
            f"{core.utils.random_string(6)}".upper()
        )
        payment.number = payment_number
        payment.save()


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0006_paymentmethod"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="number",
            field=models.CharField(
                default=core.utils.generate_payment_number, max_length=255
            ),
        ),
        migrations.RunPython(code=generate_payment_number_),
        migrations.AlterField(
            model_name="paymentmethod",
            name="name",
            field=models.CharField(
                choices=[("MPESA", "MPESA"), ("BANK", "BANK")],
                default="MPESA",
                max_length=255,
                unique=True,
            ),
        ),
        migrations.CreateModel(
            name="PaymentTransactionLogs",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateField(auto_now=True)),
                ("state", models.CharField(default="FAILED", max_length=255)),
                ("message", models.CharField(max_length=2048)),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="payments.payment",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
