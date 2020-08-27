from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from django.core.validators import RegexValidator
from dateutil.relativedelta import *

# Create your models here.
class EquipmentList(models.Model):
    CountIndex = models.AutoField(primary_key=True)
    EquipmentNo = models.CharField(max_length=255, default='')
    AssetNo = models.CharField(max_length=255, blank=True, default='', validators=[RegexValidator(r'^[A-Za-z0-9- ]+$')])
    MaximoNo = models.CharField(max_length=255, blank=True, default='', validators=[RegexValidator(r'^[A-Za-z0-9- ]+$')])
    ToolingNo = models.CharField(max_length=255,blank=True, default='', validators=[RegexValidator(r'^[A-Za-z0-9- ]+$')])
    ModuleNo = models.CharField(max_length=255, blank=True, default='', validators=[RegexValidator(r'^[A-Za-z0-9\"\/\_\-\/ ]+$')])
    Name = models.CharField(max_length=4000, blank=True, default='')
    EnName = models.CharField(max_length=4000, default='', validators=[RegexValidator(r'^[A-Za-z0-9-\*\(\)\u3000\u3400-\u4DBF\u4E00-\u9FFF ]+$')])
    SerialNumber = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9- ]+$')])
    EquipmentOwnerID = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    EquipmentOwnerName = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    EquipmentType = models.CharField(max_length=255, default='')
    TeamGroup = models.CharField(max_length=255, default='')
    ToolingGroup = models.CharField(max_length=255, default='')
    PhotoLink = models.ImageField(upload_to='photo')
    EquipmentGroup = models.CharField(max_length=255, default='')
    Location = models.CharField(max_length=255, default='')
    CreateUser = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    Site = models.CharField(max_length=255, default='')
    ProdVendor = models.CharField(max_length=255, default='')
    CreateDate = models.DateField(null=True, blank=True, default=None)
    Length = models.FloatField(null=True, default=0)
    Width = models.FloatField(null=True, default=0)
    Height = models.FloatField(null=True, default=0)
    Weight = models.FloatField(null=True, default=0)
    Status = models.CharField(max_length=255, default='')
    Cost = models.FloatField(null=True, blank=True, default=0)
    ChDescription = models.CharField(max_length=4000, blank=True, default='')
    EnDescription = models.CharField(max_length=4000, blank=True, default='')
    LimitFreezeQnty = models.IntegerField(default=1, validators=[RegexValidator(r'^[0-9]+$')])
    Specification = models.CharField(max_length=4000, blank=True, default='')
    Limitations = models.CharField(max_length=4000, blank=True, default='')

    LastCalibratedDate = models.DateField(null=True, blank=True)
    NextCalibratedDate = models.DateField(null=True, blank=True)
    PlanCalDate = models.DateField(null=True, blank=True, default=None)

    AssetLoanedReturnDate = models.DateField(null=True, blank=True, default=None)

    TransactionTicketNo = models.CharField(max_length=255, blank=True, default='')
    LastTransactionDate = models.DateField(null=True, blank=True, default=None)

    NonStockNo = models.CharField(max_length=255, blank=True, default='', validators=[RegexValidator(r'^[a-zA-Z0-9-]+$')])
    LastNonStockShipDate = models.DateField(null=True, blank=True, default=None)
    NonStockSpace = models.FloatField(null=True, blank=True, default=0)

    LastModifyDate = models.DateField(null=True, blank=True, default=None)
    LastModifyUser = models.CharField(max_length=255, default='')
    Deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.CountIndex)

class AssetLoanRecord(models.Model):
    TicketNo = models.AutoField(primary_key=True)
    AssetLoanTicketNo = models.CharField(max_length=255, default='')
    Name = models.CharField(max_length=4000, blank=True, default='')
    EnName = models.CharField(max_length=4000, default='', validators=[RegexValidator(r'^[A-Za-z0-9-\*\(\)\u3000\u3400-\u4DBF\u4E00-\u9FFF ]+$')])
    EquipmentNo = models.CharField(max_length=255, default='')
    AssetNo = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9- ]+$')])
    LoanReason = models.CharField(max_length=4000, default='')
    LoanStartTime = models.DateField(null=True, blank=True, default=None)
    LoanEndTime = models.DateField(null=True, blank=True, default=None)
    IsLongTermEvent = models.BooleanField(default=False)
    LoanVendor = models.CharField(max_length=255, default='')
    Borrower = models.CharField(max_length=255, default='')
    Value = models.FloatField(null=True, blank=True, default=0)
    Location = models.CharField(max_length=255, default='')
    AssetLoanDocument = models.FileField(blank=True, upload_to='AssetLoanDocument')
    PhotoLink = models.CharField(max_length=255, blank=True, default='')
    ActualReturnDate = models.DateField(null=True, blank=True)
    Deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.TicketNo)

class NonStockTransactionRecord(models.Model):

    TicketNo = models.AutoField(primary_key=True)
    NonStockTicketNo = models.CharField(max_length=255, default='')
    Name = models.CharField(max_length=4000, blank=True, default='')
    EnName = models.CharField(max_length=4000, default='', validators=[RegexValidator(r'^[A-Za-z0-9-\*\(\)\u3000\u3400-\u4DBF\u4E00-\u9FFF ]+$')])
    NonStockNo = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[a-zA-Z0-9- ]+$')])
    EquipmentNo = models.CharField(max_length=255, default='')
    TicketCreateTime = models.DateField(null=True, blank=True, default=None)
    TicketCreateUser = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    TransactionReqTime = models.DateField(null=True, blank=True, default=None)
    TransactionReqUser = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    TransactionFrom = models.CharField(max_length=255, default='')
    TransactionTo = models.CharField(max_length=255, default='')
    NonStockSpace = models.FloatField(null=True, blank=True, default=0)
    TruckType = models.CharField(max_length=255, default='')
    PhotoLink = models.CharField(max_length=255, blank=True, default='')
    # TicketRemark = models.CharField(max_length=255, null=True)
    Description = models.CharField(max_length=4000, null=True, blank=True, default='')
    OtherDemand = models.CharField(max_length=4000, null=True, blank=True, default='')
    # Height/Width/Length/Weight relation?
    Deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.TicketNo)

class ToolingCalibrationRecord(models.Model):

    # Needs to add WHO's CALIBRATING!
    TicketNo = models.AutoField(primary_key=True)
    CalibratedTicketNo = models.CharField(max_length=255, default='')
    EquipmentNo = models.CharField(max_length=255, default='')
    ToolingNo = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9- ]+$')])
    Name = models.CharField(max_length=4000, blank=True, default='')
    EnName = models.CharField(max_length=4000, default='', validators=[RegexValidator(r'^[A-Za-z0-9-\*\(\)\u3000\u3400-\u4DBF\u4E00-\u9FFF ]+$')])
    ModuleNo = models.CharField(max_length=255, null=True, blank=True, default='')
    Location = models.CharField(max_length=255, default='')
    ProdVendor = models.CharField(max_length=255, default='')
    PhotoLink = models.CharField(max_length=255, blank=True, default='')
    CalibratedTicketCreateDate = models.DateField(null=True, blank=True, default=None)
    CalibratedStartTime = models.DateField(null=True, blank=True, default=None)
    CaliVendor = models.CharField(max_length=255, default='')
    LastDueDate = models.DateField(null=True, blank=True, default=None)
    NextDueDate = models.DateField(null=True, blank=True, default=None)
    CalibratedReport = models.FileField(blank=True, upload_to='CalibratedReport')
    UnitPrice = models.FloatField(null=True, blank=True, default=0)
    CalibratedCost = models.FloatField(null=True, blank=True, default=0)
    ExpectedCalibratedEndTime = models.DateField(null=True, blank=True, default=None)
    ActualCalibratedEndTime = models.DateField(null=True, blank=True, default=None)
    Comment = models.CharField(max_length=4000, null=True, blank=True, default='')
    
    MQStartTime = models.DateField(null=True, blank=True, default=None)
    MQEndTime = models.DateField(null=True, blank=True, default=None)
    AvgCalibratedPeriod = models.IntegerField(null=True, blank=True, default=None)
    # CalibrateTicketRemark = models.CharField(max_length=255, null=True)
    AlertTime = models.DateField(null=True, blank=True, default=None)
    Deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.TicketNo)

class TransactionRecord(models.Model):

    TicketNo = models.AutoField(primary_key=True)
    TransactionTicketNo = models.CharField(max_length=255, default='')
    TicketCreateTime = models.DateField(null=True, blank=True, default=None)
    TicketCreateUser = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    TransactionReqTime = models.DateField(null=True, blank=True, default=None)
    TransactionReqUser = models.CharField(max_length=255, default='', validators=[RegexValidator(r'^[A-Za-z0-9 ]+$')])
    TransactionFrom = models.CharField(max_length=255, default='')
    TransactionTo = models.CharField(max_length=255, default='')
    TruckType = models.CharField(max_length=255, default='')
    PhotoLink = models.CharField(max_length=255, blank=True, default='')
    # LastTransactionDate = models.DateTimeField(null=True)   # Update to Main List
    # TicketRemark = models.CharField(max_length=255, null=True)
    Description = models.CharField(max_length=4000, default='')
    # Height/Width/Length/Weight relation?
    Deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.TicketNo)

class EquipmentGroup(models.Model):
    EquipmentGroupName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.EquipmentGroupName

class ToolingGroup(models.Model):
    ToolingGroupName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.ToolingGroupName

class TeamGroup(models.Model):
    TeamGroupName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.TeamGroupName

class Status(models.Model):
    Status = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.Status

class Location(models.Model):
    Location = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.Location

class Site(models.Model):
    Site = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.Site

class CaliVendor(models.Model):
    CaliVendorName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.CaliVendorName

class Truck(models.Model):
    Truck = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.Truck

class ProdVendor(models.Model):
    ProdVendorName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.ProdVendorName

class LoanVendor(models.Model):
    LoanVendorName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.LoanVendorName

class Borrower(models.Model):
    BorrowerName = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.BorrowerName

class ActionLog(models.Model):
    User = models.CharField(max_length=255, default='')
    Action = models.TextField(default='')
    Date = models.DateField(null=True, blank=True, default=None)
    Time = models.TimeField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.User)

class AssetQnty(models.Model):
    Year = models.CharField(max_length=255, default=None)
    Month = models.CharField(max_length=255, default=None)
    Day = models.CharField(max_length=255, default=None)
    Quantity = models.IntegerField(default=None)

    def __str__(self):
        return str(self.Quantity)

class ToolQnty(models.Model):
    Year = models.CharField(max_length=255, default=None)
    Month = models.CharField(max_length=255, default=None)
    Day = models.CharField(max_length=255, default=None)
    Quantity = models.IntegerField(default=None)
    
    def __str__(self):
        return str(self.Quantity)

class NonStockQnty(models.Model):
    Year = models.CharField(max_length=255, default=None)
    Month = models.CharField(max_length=255, default=None)
    Day = models.CharField(max_length=255, default=None)
    Quantity = models.IntegerField(default=None)
    
    def __str__(self):
        return str(self.Quantity)