# Generated by Django 5.1.7 on 2025-05-22 10:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_lead_reference"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="user_reply",
            field=models.TextField(null=True),
        ),
    ]
