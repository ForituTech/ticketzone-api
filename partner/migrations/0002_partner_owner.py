# Generated by Django 4.0.2 on 2022-02-04 17:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="owner",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owner",
                to="partner.person",
            ),
            preserve_default=False,
        ),
    ]
