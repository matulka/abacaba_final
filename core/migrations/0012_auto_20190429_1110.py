# Generated by Django 2.1.4 on 2019-04-29 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20190429_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='product',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Product'),
        ),
    ]
