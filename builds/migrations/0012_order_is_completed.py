# Generated by Django 4.2.12 on 2025-06-12 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("builds", "0011_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_completed",
            field=models.BooleanField(default=False, verbose_name="Заказ выдан"),
        ),
    ]
