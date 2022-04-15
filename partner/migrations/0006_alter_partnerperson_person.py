# Generated by Django 4.0.3 on 2022-04-15 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0005_remove_partner_banking_info_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partnerperson",
            name="person",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="membership",
                to="partner.person",
            ),
        ),
    ]
