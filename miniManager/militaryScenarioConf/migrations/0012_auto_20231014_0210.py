# Generated by Django 3.2.6 on 2023-10-14 02:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('militaryScenarioConf', '0011_remove_platform_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='militaryorganization',
            options={'verbose_name': 'MilitaryOrganization', 'verbose_name_plural': 'MilitaryOrganizations'},
        ),
        migrations.RenameField(
            model_name='militaryorganization',
            old_name='type',
            new_name='MOPowerType',
        ),
    ]