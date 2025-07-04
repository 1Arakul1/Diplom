# Generated by Django 4.2.12 on 2025-06-12 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("builds", "0010_order_alter_build_options_alter_cartitem_build_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Заказ на рассмотрении"),
                    ("confirmed", "Заказ подтверждён"),
                    ("assembling", "Заказ собирается"),
                    ("delivered", "Заказ доставлен, заберите его"),
                ],
                default="pending",
                max_length=20,
                verbose_name="Статус заказа",
            ),
        ),
    ]
