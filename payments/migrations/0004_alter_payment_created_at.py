# Generated by Django 4.0.4 on 2022-05-14 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_alter_payment_made_through"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
