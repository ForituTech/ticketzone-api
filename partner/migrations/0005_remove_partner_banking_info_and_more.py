# Generated by Django 4.0.3 on 2022-03-28 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0004_alter_partner_banking_info"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="partner",
            name="banking_info",
        ),
        migrations.AddField(
            model_name="partner",
            name="bank_account_number",
            field=models.CharField(default="1", max_length=512),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="partner",
            name="bank_code",
            field=models.CharField(default="1", max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="PartnerBankingInfo",
        ),
    ]
