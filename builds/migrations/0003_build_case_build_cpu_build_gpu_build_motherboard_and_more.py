# Generated by Django 4.2.12 on 2025-06-02 10:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0004_build'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('builds', '0002_remove_build_case_remove_build_cpu_remove_build_gpu_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='case',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.case', verbose_name='Case'),
        ),
        migrations.AddField(
            model_name='build',
            name='cpu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.cpu', verbose_name='CPU'),
        ),
        migrations.AddField(
            model_name='build',
            name='gpu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.gpu', verbose_name='GPU'),
        ),
        migrations.AddField(
            model_name='build',
            name='motherboard',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.motherboard', verbose_name='Motherboard'),
        ),
        migrations.AddField(
            model_name='build',
            name='psu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.psu', verbose_name='PSU'),
        ),
        migrations.AddField(
            model_name='build',
            name='ram',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.ram', verbose_name='RAM'),
        ),
        migrations.AddField(
            model_name='build',
            name='storage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='components.storage', verbose_name='Storage'),
        ),
        migrations.AddField(
            model_name='build',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
            preserve_default=False,
        ),
    ]
