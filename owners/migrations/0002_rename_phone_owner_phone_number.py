# Generated by Django 4.0.3 on 2022-03-20 01:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("owners", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="owner",
            old_name="phone",
            new_name="phone_number",
        ),
    ]