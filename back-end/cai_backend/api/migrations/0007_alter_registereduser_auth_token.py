# Generated by Django 5.1.6 on 2025-03-18 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_remove_registereduser_last_login_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registereduser",
            name="auth_token",
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
    ]
