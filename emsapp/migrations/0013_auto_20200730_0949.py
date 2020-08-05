# Generated by Django 2.1.10 on 2020-07-30 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emsapp', '0012_auto_20200728_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EquipmentGroupName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Location', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ModuleNo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ModuleNo', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Site', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Status', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TeamGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamGroupName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ToolingGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ToolingGroupName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Truck', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Vendor', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='toolingcalibrationrecord',
            name='Department',
        ),
        migrations.AlterField(
            model_name='assetloanrecord',
            name='LoanStartTime',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='equipmentlist',
            name='CreateDate',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='equipmentlist',
            name='EquipmentGroup',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='equipmentlist',
            name='LastModifyDate',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='equipmentlist',
            name='LastNonStockShipDate',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='nonstocktransactionrecord',
            name='TicketCreateTime',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='nonstocktransactionrecord',
            name='TransactionReqTime',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='toolingcalibrationrecord',
            name='CalibratedStartTime',
            field=models.DateField(default='2020-07-30'),
        ),
        migrations.AlterField(
            model_name='toolingcalibrationrecord',
            name='CalibratedTicketCreateDate',
            field=models.DateField(default='2020-07-30'),
        ),
    ]
