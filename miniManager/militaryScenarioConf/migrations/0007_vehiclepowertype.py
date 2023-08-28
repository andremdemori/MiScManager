# Generated by Django 3.2.6 on 2023-08-28 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militaryScenarioConf', '0006_auto_20230828_2057'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehiclePowerType',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'VehiclePowerType',
                'verbose_name_plural': 'VehiclePowerTypes',
                'db_table': 'VehiclePowerType',
            },
        ),
    ]
