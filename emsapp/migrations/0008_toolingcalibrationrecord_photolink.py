# Generated by Django 2.1.10 on 2020-07-28 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emsapp', '0007_remove_toolingcalibrationrecord_photolink'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolingcalibrationrecord',
            name='PhotoLink',
            field=models.CharField(default='', max_length=255),
        ),
    ]
