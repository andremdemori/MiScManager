# Generated by Django 3.2.6 on 2023-03-19 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0041_alter_commdevicecarrier_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='MilitaryAsCarrier',
            fields=[
                ('commdevicecarrier_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='configurator.commdevicecarrier')),
                ('Id_mc', models.AutoField(primary_key=True, serialize=False, unique=True)),
            ],
            bases=('configurator.commdevicecarrier',),
        ),
        migrations.RemoveField(
            model_name='commdevicecarrier',
            name='type',
        ),
    ]