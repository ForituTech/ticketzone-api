# Generated by Django 4.1.7 on 2023-03-19 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("partner_api", "0003_paymentintent_redirect_to"),
    ]

    operations = [
        migrations.RenameField(
            model_name="paymentintent",
            old_name="redirect_to",
            new_name="callback_url",
        ),
    ]
