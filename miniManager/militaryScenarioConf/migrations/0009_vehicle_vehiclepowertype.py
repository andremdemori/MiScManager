# Generated by Django 3.2.6 on 2023-08-28 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('militaryScenarioConf', '0008_rename_guarani_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='VehiclePowerType',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.vehiclepowertype'),
            preserve_default=False,
        ),
    ]
