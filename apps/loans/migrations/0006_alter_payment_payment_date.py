# Generated by Django 4.2.4 on 2024-04-04 01:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("loans", "0005_alter_payment_payment_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="payment_date",
            field=models.DateTimeField(
                default=datetime.datetime(2024, 4, 4, 9, 57, 5, 914033), null=True
            ),
        ),
    ]
