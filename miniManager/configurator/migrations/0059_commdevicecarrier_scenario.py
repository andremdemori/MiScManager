# Generated by Django 3.2.6 on 2023-04-03 14:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0058_interfacepowertype'),
    ]

    operations = [
        migrations.AddField(
            model_name='commdevicecarrier',
            name='scenario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='configurator.militaryscenario'),
        ),
    ]
