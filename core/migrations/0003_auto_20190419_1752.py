# Generated by Django 2.1.4 on 2019-04-19 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190419_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sample_image',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
        migrations.AlterField(
            model_name='stockproduct',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
    ]
