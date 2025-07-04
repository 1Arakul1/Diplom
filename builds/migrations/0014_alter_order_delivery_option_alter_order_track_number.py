# Generated by Django 4.2.12 on 2025-06-13 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("builds", "0013_alter_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="delivery_option",
            field=models.CharField(
                choices=[
                    ("pickup", "Самовывоз из магазина"),
                    ("courier", "Доставка курьером"),
                ],
                max_length=50,
                verbose_name="Способ доставки",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="track_number",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=8,
                null=True,
                unique=True,
                verbose_name="Трек-номер",
            ),
        ),
    ]
