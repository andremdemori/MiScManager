# Generated by Django 3.2.6 on 2023-08-28 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('militaryScenarioConf', '0004_auto_20230828_1942'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MilitaryOrganizationPowerType',
            new_name='UnitPowerType',
        ),
        migrations.AlterModelOptions(
            name='unitpowertype',
            options={'verbose_name': 'UnitPowerType', 'verbose_name_plural': 'UnitPowerTypes'},
        ),
        migrations.AlterModelTable(
            name='unitpowertype',
            table='UnitPowerType',
        ),
    ]
