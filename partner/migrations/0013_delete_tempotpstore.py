# Generated by Django 4.1.7 on 2023-04-20 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0012_partner_verified"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TempOTPStore",
        ),
    ]
