# Generated by Django 3.2.6 on 2022-06-30 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configurator', '0004_remove_accesspoint_wlans'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesspoint',
            name='wlans',
            field=models.CharField(default=2, max_length=30),
            preserve_default=False,
        ),
    ]
