# Generated by Django 2.1.10 on 2020-08-05 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emsapp', '0031_auto_20200805_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetloanrecord',
            name='LoanEndTime',
            field=models.DateField(default='2021-02-05'),
        ),
        migrations.AlterField(
            model_name='toolingcalibrationrecord',
            name='CalibratedEndTime',
            field=models.DateField(default='2020-08-19'),
        ),
    ]
