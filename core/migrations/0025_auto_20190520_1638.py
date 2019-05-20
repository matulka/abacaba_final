# Generated by Django 2.1.4 on 2019-05-20 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_merge_20190518_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='product',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='image', to='core.Product'),
        ),
    ]