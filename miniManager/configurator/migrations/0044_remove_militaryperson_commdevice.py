# Generated by Django 3.2.6 on 2023-03-20 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0043_commdevicecarrier_visibilityrange'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='militaryperson',
            name='CommDevice',
        ),
    ]