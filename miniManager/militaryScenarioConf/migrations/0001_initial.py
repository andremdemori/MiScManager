# Generated by Django 3.2.6 on 2023-04-03 23:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommDevice_Carrier',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('VisibilityRange', models.FloatField(blank=True, max_length=30, null=True)),
                ('v_min', models.FloatField(blank=True, max_length=30, null=True)),
                ('v_max', models.FloatField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Military_Organization',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('commander', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_organization')),
            ],
            options={
                'verbose_name': 'Military_Organization',
                'verbose_name_plural': 'Military_Organization',
                'db_table': 'Military_Organization',
            },
        ),
        migrations.CreateModel(
            name='Military_Scenario',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Military_Scenario',
                'verbose_name_plural': 'Military_Scenario',
                'db_table': 'Military_Scenario',
            },
        ),
        migrations.CreateModel(
            name='MilitaryPerson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Identifier', models.CharField(max_length=30)),
                ('CommDevice_Carrier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commdevicecarrier', to='militaryScenarioConf.commdevice_carrier')),
                ('Military_Organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_organization')),
                ('scenario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_scenario')),
            ],
            options={
                'verbose_name': 'Military_Person',
                'verbose_name_plural': 'Military_Person',
                'db_table': 'Military_Person',
            },
        ),
        migrations.CreateModel(
            name='Military_OrganizationPowerType',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('commander', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_organizationpowertype')),
            ],
            options={
                'verbose_name': 'Military_OrganizationPowerType',
                'verbose_name_plural': 'Military_OrganizationPowerTypes',
                'db_table': 'Military_OrganizationPowerType',
            },
        ),
        migrations.AddField(
            model_name='military_organization',
            name='scenario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_scenario'),
        ),
        migrations.AddField(
            model_name='military_organization',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_organizationpowertype'),
        ),
        migrations.AddField(
            model_name='commdevice_carrier',
            name='scenario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_scenario'),
        ),
        migrations.CreateModel(
            name='MilitaryPlatform',
            fields=[
                ('commdevice_carrier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='militaryScenarioConf.commdevice_carrier')),
                ('category', models.CharField(choices=[('armored', 'Armored')], default='armored', max_length=30)),
                ('kind', models.CharField(max_length=30)),
                ('Military_Organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='militaryScenarioConf.military_organization')),
            ],
            bases=('militaryScenarioConf.commdevice_carrier',),
        ),
    ]
