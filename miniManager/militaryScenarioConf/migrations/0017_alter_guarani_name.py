# Generated by Django 3.2.6 on 2023-05-20 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('militaryScenarioConf', '0016_alter_guarani_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarani',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
