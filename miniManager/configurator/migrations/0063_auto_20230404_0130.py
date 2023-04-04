# Generated by Django 3.2.6 on 2023-04-04 01:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('militaryScenarioConf', '0002_auto_20230403_2318'),
        ('configurator', '0062_alter_node_militaryperson'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='militaryorganization',
            name='commander',
        ),
        migrations.RemoveField(
            model_name='militaryorganization',
            name='scenario',
        ),
        migrations.RemoveField(
            model_name='militaryorganization',
            name='type',
        ),
        migrations.RemoveField(
            model_name='militaryorganizationpowertype',
            name='commander',
        ),
        migrations.RemoveField(
            model_name='militaryperson',
            name='CommDeviceCarrier',
        ),
        migrations.RemoveField(
            model_name='militaryperson',
            name='MilitaryOrganization',
        ),
        migrations.RemoveField(
            model_name='militaryperson',
            name='scenario',
        ),
        migrations.RemoveField(
            model_name='militaryplatform',
            name='MilitaryOrganization',
        ),
        migrations.RemoveField(
            model_name='militaryplatform',
            name='commdevicecarrier_ptr',
        ),
        migrations.AlterField(
            model_name='testplan',
            name='scenario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_scenario'),
        ),
        migrations.DeleteModel(
            name='CommDeviceCarrier',
        ),
        migrations.DeleteModel(
            name='MilitaryOrganization',
        ),
        migrations.DeleteModel(
            name='MilitaryOrganizationPowerType',
        ),
        migrations.DeleteModel(
            name='MilitaryPerson',
        ),
        migrations.DeleteModel(
            name='MilitaryPlatform',
        ),
        migrations.DeleteModel(
            name='MilitaryScenario',
        ),
    ]
