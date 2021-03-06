# Generated by Django 2.1.4 on 2019-05-09 22:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0018_addresses_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addresses',
            name='customers',
        ),
        migrations.AddField(
            model_name='addresses',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='addresses',
            name='building',
            field=models.IntegerField(default=1),
        ),
    ]
