# Generated by Django 2.1.10 on 2020-07-28 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emsapp', '0009_auto_20200728_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toolingcalibrationrecord',
            name='UnitPrice',
            field=models.FloatField(default=None, null=True),
        ),
    ]
