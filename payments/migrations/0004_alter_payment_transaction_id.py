# Generated by Django 4.0.2 on 2022-03-06 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_remove_payment_made_at_alter_payment_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="transaction_id",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]