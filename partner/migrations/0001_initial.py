# Generated by Django 4.0.2 on 2022-02-19 13:52

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PartnerBankingInfo",
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
                ("created_at", models.DateField(auto_now_add=True)),
                ("updated_at", models.DateField(auto_now=True)),
                ("bank_code", models.IntegerField()),
                ("bank_account_number", models.BigIntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Person",
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
                ("created_at", models.DateField(auto_now_add=True)),
                ("updated_at", models.DateField(auto_now=True)),
                ("name", models.CharField(max_length=256)),
                (
                    "email",
                    models.CharField(
                        default="0", max_length=256, verbose_name="E-mail"
                    ),
                ),
                ("phone_number", models.CharField(max_length=15)),
                (
                    "person_type",
                    models.CharField(
                        choices=[
                            ("PR", "PARTNER"),
                            ("TA", "TICKETING_AGENT"),
                            ("CR", "CUSTOMER"),
                        ],
                        default="CR",
                        max_length=255,
                    ),
                ),
                ("hashed_password", models.CharField(max_length=1024)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Partner",
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
                ("created_at", models.DateField(auto_now_add=True)),
                ("updated_at", models.DateField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "banking_info",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="partner.partnerbankinginfo",
                    ),
                ),
                (
                    "contact_person",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="partner.person",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner",
                        to="partner.person",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
