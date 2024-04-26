# Generated by Django 5.0.4 on 2024-04-26 00:33

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Rate",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("base_currency", models.CharField(max_length=3)),
                ("target_currency", models.CharField(max_length=3)),
                ("rate", models.FloatField()),
                ("timestamp", models.DateTimeField(verbose_name="date checked")),
            ],
        ),
    ]
