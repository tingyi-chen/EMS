# Generated by Django 2.1.10 on 2020-08-19 03:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('User', models.CharField(default='', max_length=255)),
                ('Action', models.TextField(default='')),
                ('Date', models.DateField(blank=True, default=None, null=True)),
                ('Time', models.TimeField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetLoanRecord',
            fields=[
                ('TicketNo', models.AutoField(primary_key=True, serialize=False)),
                ('AssetLoanTicketNo', models.CharField(default='', max_length=255)),
                ('EquipmentNo', models.CharField(default='', max_length=255)),
                ('AssetNo', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$')])),
                ('LoanReason', models.CharField(default='', max_length=255)),
                ('LoanStartTime', models.DateField(blank=True, default=None, null=True)),
                ('LoanEndTime', models.DateField(blank=True, default=None, null=True)),
                ('IsLongTermEvent', models.BooleanField(default=True)),
                ('LoanVendor', models.CharField(default='', max_length=255)),
                ('Borrower', models.CharField(default='', max_length=255)),
                ('Value', models.FloatField(blank=True, default=0, null=True)),
                ('Location', models.CharField(default='', max_length=255)),
                ('AssetLoanDocument', models.FileField(blank=True, upload_to='')),
                ('PhotoLink', models.CharField(default='', max_length=255)),
                ('ActualReturnDate', models.DateField(blank=True, null=True)),
                ('Deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Borrower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BorrowerName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CaliVendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CaliVendorName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('EquipmentGroupName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EquipmentList',
            fields=[
                ('CountIndex', models.AutoField(primary_key=True, serialize=False)),
                ('EquipmentNo', models.CharField(default='', max_length=255)),
                ('AssetNo', models.CharField(blank=True, default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-]+$')])),
                ('MaximoNo', models.CharField(blank=True, default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-]+$')])),
                ('ToolingNo', models.CharField(blank=True, default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-]+$')])),
                ('ModuleNo', models.CharField(blank=True, default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9\\"\\/\\_\\-\\/]+$')])),
                ('Name', models.CharField(default='', max_length=255)),
                ('EnName', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-\\*\\(\\)\\u3000\\u3400-\\u4DBF\\u4E00-\\u9FFF ]+$')])),
                ('SerialNumber', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[0-9]+$')])),
                ('EquipmentOwnerID', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$')])),
                ('EquipmentOwnerName', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9 ]+$')])),
                ('EquipmentType', models.CharField(default='', max_length=255)),
                ('TeamGroup', models.CharField(default='', max_length=255)),
                ('ToolingGroup', models.CharField(default='', max_length=255)),
                ('PhotoLink', models.ImageField(upload_to='')),
                ('EquipmentGroup', models.CharField(default='', max_length=255)),
                ('Location', models.CharField(default='', max_length=255)),
                ('CreateUser', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9 ]+$')])),
                ('Site', models.CharField(default='', max_length=255)),
                ('ProdVendor', models.CharField(default='', max_length=255)),
                ('CreateDate', models.DateField(blank=True, default=None, null=True)),
                ('Length', models.FloatField(default=0, null=True)),
                ('Width', models.FloatField(default=0, null=True)),
                ('Height', models.FloatField(default=0, null=True)),
                ('Weight', models.FloatField(default=0, null=True)),
                ('Status', models.CharField(default='', max_length=255)),
                ('Cost', models.FloatField(blank=True, default=0, null=True)),
                ('ChDescription', models.CharField(blank=True, default='', max_length=255)),
                ('EnDescription', models.CharField(blank=True, default='', max_length=255)),
                ('LimitFreezeQnty', models.IntegerField(default=1, validators=[django.core.validators.RegexValidator('^[0-9]+$')])),
                ('Specification', models.CharField(blank=True, default='', max_length=255)),
                ('Limitations', models.CharField(blank=True, default='', max_length=255)),
                ('LastCalibratedDate', models.DateField(blank=True, null=True)),
                ('NextCalibratedDate', models.DateField(blank=True, null=True)),
                ('PlanCalDate', models.DateField(blank=True, default=None, null=True)),
                ('AssetLoanedReturnDate', models.DateField(blank=True, default=None, null=True)),
                ('TransactionTicketNo', models.CharField(blank=True, default='', max_length=255)),
                ('LastTransactionDate', models.DateField(blank=True, default=None, null=True)),
                ('NonStockNo', models.CharField(blank=True, default='', max_length=255, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9-]+$')])),
                ('LastNonStockShipDate', models.DateField(blank=True, default=None, null=True)),
                ('NonStockSpace', models.FloatField(blank=True, default=0, null=True)),
                ('LastModifyDate', models.DateField(blank=True, default=None, null=True)),
                ('LastModifyUser', models.CharField(default='', max_length=255)),
                ('Deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LoanVendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LoanVendorName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Location', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='NonStockTransactionRecord',
            fields=[
                ('TicketNo', models.AutoField(primary_key=True, serialize=False)),
                ('NonStockTicketNo', models.CharField(default='', max_length=255)),
                ('NonStockNo', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9-]+$')])),
                ('EquipmentNo', models.CharField(default='', max_length=255)),
                ('TicketCreateTime', models.DateField(blank=True, default=None, null=True)),
                ('TicketCreateUser', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$')])),
                ('TransactionReqTime', models.DateField(blank=True, default=None, null=True)),
                ('TransactionReqUser', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$')])),
                ('TransactionFrom', models.CharField(default='', max_length=255)),
                ('TransactionTo', models.CharField(default='', max_length=255)),
                ('NonStockSpace', models.FloatField(blank=True, default=0, null=True)),
                ('TruckType', models.CharField(default='', max_length=255)),
                ('Description', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('OtherDemand', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('Deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProdVendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ProdVendorName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Site', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Status', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TeamGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TeamGroupName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ToolingCalibrationRecord',
            fields=[
                ('TicketNo', models.AutoField(primary_key=True, serialize=False)),
                ('CalibratedTicketNo', models.CharField(default='', max_length=255)),
                ('EquipmentNo', models.CharField(default='', max_length=255)),
                ('ToolingNo', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[0-9]+$')])),
                ('Name', models.CharField(default='', max_length=255)),
                ('EnName', models.CharField(default='', max_length=255)),
                ('ModuleNo', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('Location', models.CharField(default='', max_length=255)),
                ('ProdVendor', models.CharField(default='', max_length=255)),
                ('PhotoLink', models.CharField(default='', max_length=255)),
                ('CalibratedTicketCreateDate', models.DateField(blank=True, default=None, null=True)),
                ('CalibratedStartTime', models.DateField(blank=True, default=None, null=True)),
                ('CaliVendor', models.CharField(default='', max_length=255)),
                ('LastDueDate', models.DateField(blank=True, default=None, null=True)),
                ('NextDueDate', models.DateField(blank=True, default=None, null=True)),
                ('CalibratedReport', models.FileField(blank=True, upload_to='')),
                ('UnitPrice', models.FloatField(blank=True, default=0, null=True)),
                ('CalibratedCost', models.FloatField(blank=True, default=0, null=True)),
                ('ExpectedCalibratedEndTime', models.DateField(blank=True, default=None, null=True)),
                ('ActualCalibratedEndTime', models.DateField(blank=True, default=None, null=True)),
                ('Comment', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('MQStartTime', models.DateField(blank=True, default=None, null=True)),
                ('MQEndTime', models.DateField(blank=True, default=None, null=True)),
                ('AvgCalibratedPeriod', models.IntegerField(blank=True, default=None, null=True)),
                ('AlertTime', models.DateField(blank=True, default=None, null=True)),
                ('Deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ToolingGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ToolingGroupName', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionRecord',
            fields=[
                ('TicketNo', models.AutoField(primary_key=True, serialize=False)),
                ('TransactionTicketNo', models.CharField(default='', max_length=255)),
                ('TicketCreateTime', models.DateField(blank=True, default=None, null=True)),
                ('TicketCreateUser', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$')])),
                ('TransactionReqTime', models.DateField(blank=True, default=None, null=True)),
                ('TransactionReqUser', models.CharField(default='', max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9]+$')])),
                ('TransactionFrom', models.CharField(default='', max_length=255)),
                ('TransactionTo', models.CharField(default='', max_length=255)),
                ('TruckType', models.CharField(default='', max_length=255)),
                ('Description', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('Deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Truck', models.CharField(default='', max_length=255)),
            ],
        ),
    ]
