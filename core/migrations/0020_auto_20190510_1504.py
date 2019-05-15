# Generated by Django 2.1.4 on 2019-05-10 15:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20190509_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addresses',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='addresses',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]