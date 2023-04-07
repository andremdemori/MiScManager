# Generated by Django 3.2.6 on 2023-04-02 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0053_delete_militaryascarrier'),
    ]

    operations = [
        migrations.CreateModel(
            name='MilitaryOrganizationPowerType',
            fields=[
                ('Id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('commander', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='configurator.militaryorganization')),
            ],
            options={
                'verbose_name': 'MilitaryOrganizationPowerType',
                'verbose_name_plural': 'MilitaryOrganizationPowerTypes',
                'db_table': 'MilitaryOrganizationPowerType',
            },
        ),
    ]