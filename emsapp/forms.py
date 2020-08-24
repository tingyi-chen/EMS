from django import forms
from .models import EquipmentList, NonStockTransactionRecord, AssetLoanRecord, ToolingCalibrationRecord, EquipmentGroup, ToolingGroup, Location, Site, Status, TeamGroup, Truck, CaliVendor, ProdVendor, LoanVendor, Borrower, TransactionRecord
import datetime
from bootstrap_datepicker_plus import DatePickerInput
from tempus_dominus.widgets import DatePicker
from dateutil.relativedelta import *

class EquipmentForm(forms.ModelForm):
    TYPE_CHOICES = (
        ('Asset', 'Asset'),
        ('Tool', 'Tool'),
        ('NonS', 'NonS'),
        ('Others', 'Others')
    )
    
    class Meta:    
        model = EquipmentList
        fields = '__all__'
        exclude = ['Deleted']
        widgets = {
            'LastNonStockShipDate': DatePickerInput(format='%Y-%m-%d'),
            'LastCalibratedDate': DatePickerInput(format='%Y-%m-%d'),
            'NextCalibratedDate': DatePickerInput(format='%Y-%m-%d'),
            'PlanCalDate': DatePickerInput(format='%Y-%m-%d'),
            'AssetLoanedReturnDate': DatePickerInput(format='%Y-%m-%d'),
            'LastTransactionDate': DatePickerInput(format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        eqno = kwargs.pop('eqno', None)
        date = kwargs.pop('date', None)
        update = kwargs.pop('update', None)
        if update:
            kwargs['initial'] = {'EquipmentNo': eqno, 'CreateUser': user, 'CreateDate': date}
        kwargs['initial'] = {'EquipmentNo': eqno}
        super(EquipmentForm, self).__init__(*args, **kwargs)
        location = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        prod_vendor = [(i['ProdVendorName'], i['ProdVendorName']) for i in ProdVendor.objects.values('ProdVendorName').distinct()]
        team_group = [(i['TeamGroupName'], i['TeamGroupName']) for i in TeamGroup.objects.values('TeamGroupName').distinct()]
        e_group = [(i['EquipmentGroupName'], i['EquipmentGroupName']) for i in EquipmentGroup.objects.values('EquipmentGroupName').distinct()]
        t_group = [(i['ToolingGroupName'], i['ToolingGroupName']) for i in ToolingGroup.objects.values('ToolingGroupName').distinct()]
        status = [(i['Status'], i['Status']) for i in Status.objects.values('Status').distinct()]
        site = [(i['Site'], i['Site']) for i in Site.objects.values('Site').distinct()]
        self.fields['EquipmentNo'].widget.attrs['readonly'] = True
        self.fields['LastModifyUser'].widget.attrs['readonly'] = True
        self.fields['LastModifyUser'].initial = user
        self.fields['LastModifyDate'].widget.attrs['readonly'] = True
        self.fields['CreateUser'].initial = user
        self.fields['CreateDate'].initial = datetime.date.today().strftime('%Y-%m-%d')
        self.fields['EquipmentType'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=self.TYPE_CHOICES)
        self.fields['EquipmentType'].label = "EquipmentType"
        self.fields['PhotoLink'].widget = forms.FileInput(attrs={'multiple': True, 'required': True})
        self.fields['EquipmentGroup'] = forms.ChoiceField(choices=e_group)
        self.fields['ToolingGroup'] = forms.ChoiceField(choices=t_group)
        self.fields['ToolingGroup'].label = "ToolingGroup"
        self.fields['TeamGroup'] = forms.ChoiceField(choices=team_group)
        self.fields['TeamGroup'].label = "TeamGroup"
        self.fields['Status'] = forms.ChoiceField(choices=status)
        self.fields['Site'] = forms.ChoiceField(choices=site)
        self.fields['Location'] = forms.ChoiceField(choices=location)
        self.fields['ProdVendor'] = forms.ChoiceField(choices=prod_vendor)
        self.fields['ProdVendor'].label = "ProdVendor"
        self.fields['LastModifyDate'].initial = datetime.date.today().strftime('%Y-%m-%d')

class AssetLoanRecordForm(forms.ModelForm):
    class Meta:
        model = AssetLoanRecord
        fields = '__all__'
        exclude = ['Deleted']
        widgets = {
            'LoanStartTime': DatePickerInput(format='%Y-%m-%d'),
            'LoanEndTime': DatePickerInput(format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        atno = kwargs.pop('atno', None)
        eqno = kwargs.pop('eqno', None)
        asno = kwargs.pop('asno', None)
        photo = kwargs.pop('photo', None)
        location = kwargs.pop('location', None)
        name = kwargs.pop('name', None)
        en_name = kwargs.pop('en_name', None)
        kwargs['initial'] = {'AssetLoanTicketNo': atno, 'EquipmentNo': eqno, 'AssetNo': asno, 'PhotoLink': photo, 'Location': location, 'Name': name, 'EnName': en_name}
        super(AssetLoanRecordForm, self).__init__(*args, **kwargs)
        location = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        vendor = [(i['LoanVendorName'], i['LoanVendorName']) for i in LoanVendor.objects.values('LoanVendorName').distinct()]
        borrower = [(i['BorrowerName'], i['BorrowerName']) for i in Borrower.objects.values('BorrowerName').distinct()]
        self.fields['EquipmentNo'].widget.attrs['readonly'] = True
        self.fields['AssetLoanTicketNo'].widget.attrs['readonly'] = True
        self.fields['AssetNo'].widget.attrs['readonly'] = True
        self.fields['Name'].widget.attrs['readonly'] = True
        self.fields['EnName'].widget.attrs['readonly'] = True
        self.fields['PhotoLink'].widget = forms.TextInput(attrs={'readonly': True, 'required': False})
        self.fields['Location'].widget.attrs['readonly'] = True
        self.fields['Borrower'] = forms.ChoiceField(choices=borrower)
        self.fields['LoanVendor'] = forms.ChoiceField(choices=vendor)
        self.fields['LoanStartTime'].initial = datetime.date.today().strftime('%Y-%m-%d')
        self.fields['LoanEndTime'].initial = (datetime.date.today() + relativedelta(months=6)).strftime('%Y-%m-%d')
        
class NonStockTransactionRecordForm(forms.ModelForm):
    class Meta:
        model = NonStockTransactionRecord
        fields = '__all__'
        exclude = ['Deleted']
        widgets = {
            'TicketCreateDate': DatePickerInput(format='%Y-%m-%d'),
            'TransactionReqTime': DatePickerInput(format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        ntno = kwargs.pop('ntno', None)
        eqno = kwargs.pop('eqno', None)
        nonstock_space = kwargs.pop('nonstock_space', None)
        nsno = kwargs.pop('nsno', None)
        photo = kwargs.pop('photo', None)
        name = kwargs.pop('name', None)
        en_name = kwargs.pop('en_name', None)
        kwargs['initial'] = {'NonStockTicketNo': ntno, 'EquipmentNo': eqno, 'NonStockSpace': nonstock_space, 'NonStockNo': nsno, 'PhotoLink': photo, 'Name': name, 'EnName': en_name}
        super(NonStockTransactionRecordForm, self).__init__(*args, **kwargs)
        trans_from = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        trans_to = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        truck_type = [(i['Truck'], i['Truck']) for i in Truck.objects.values('Truck').distinct()]
        self.fields['EquipmentNo'].widget.attrs['readonly'] = True
        self.fields['NonStockTicketNo'].widget.attrs['readonly'] = True
        self.fields['PhotoLink'].widget.attrs['readonly'] = True
        self.fields['Name'].widget.attrs['readonly'] = True
        self.fields['EnName'].widget.attrs['readonly'] = True
        self.fields['TicketCreateUser'].initial = user
        self.fields['TransactionReqUser'].initial = user
        self.fields['TransactionFrom'] = forms.ChoiceField(choices=trans_from)
        self.fields['TransactionTo'] = forms.ChoiceField(choices=trans_to)
        self.fields['TruckType'] = forms.ChoiceField(choices=truck_type)
        self.fields['NonStockSpace'].widget.attrs['readonly'] = True
        self.fields['NonStockNo'].widget.attrs['readonly'] = True
        self.fields['TransactionFrom'].label = "TransactionFrom"
        self.fields['TransactionTo'].label = "TransactionTo"
        self.fields['TruckType'].label = "TruckType"
        self.fields['TransactionReqTime'].initial = datetime.date.today().strftime('%Y-%m-%d')
        self.fields['TicketCreateTime'].initial = datetime.date.today().strftime('%Y-%m-%d')

class ToolingCalibrationRecordForm(forms.ModelForm):
    class Meta:
        model = ToolingCalibrationRecord
        fields = '__all__'
        exclude = ['Deleted']
        widgets = {
            'CalibratedTicketCreateDate': DatePickerInput(format='%Y-%m-%d'),
            'CalibratedStartTime': DatePickerInput(format='%Y-%m-%d'),
            'CalibratedEndTime': DatePickerInput(format='%Y-%m-%d'),
            'LastDueDate': DatePickerInput(format='%Y-%m-%d'),
            'NextDueDate': DatePickerInput(format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        tcno = kwargs.pop('tcno', None)
        eqno = kwargs.pop('eqno', None)
        tlno = kwargs.pop('tlno', None)
        name = kwargs.pop('name', None)
        en_name = kwargs.pop('en_name', None)
        mdno = kwargs.pop('mdno', None)
        site = kwargs.pop('site', None)
        photo = kwargs.pop('photo', None)
        pr_vendor = kwargs.pop('pr_vendor', None)
        location = kwargs.pop('location', None)
        last_due_date = kwargs.pop('last_due_date', None)
        next_due_date = kwargs.pop('next_due_date', None)
        kwargs['initial'] = {'CalibratedTicketNo': tcno, 'EquipmentNo': eqno, 'ToolingNo': tlno, 'Name': name, 'EnName': en_name, 'ModuleNo': mdno, 'PhotoLink': photo, 'site': site, 'ProdVendor': pr_vendor, 'Location': location, 'LastDueDate': last_due_date, 'NextDueDate': next_due_date}
        super(ToolingCalibrationRecordForm, self).__init__(*args, **kwargs)
        prod_vendor = [(i['ProdVendorName'], i['ProdVendorName']) for i in ProdVendor.objects.values('ProdVendorName').distinct()]
        cali_vendor = [(i['CaliVendorName'], i['CaliVendorName']) for i in CaliVendor.objects.values('CaliVendorName').distinct()]
        self.fields['CalibratedTicketNo'].widget.attrs['readonly'] = True
        self.fields['EquipmentNo'].widget.attrs['readonly'] = True
        self.fields['ToolingNo'].widget.attrs['readonly'] = True
        self.fields['Name'].widget.attrs['readonly'] = True
        self.fields['EnName'].widget.attrs['readonly'] = True
        self.fields['ProdVendor'].widget.attrs['readonly'] = True
        self.fields['PhotoLink'].widget = forms.TextInput(attrs={'readonly': True, 'required': False})
        self.fields['CaliVendor'] = forms.ChoiceField(choices=cali_vendor)
        self.fields['CaliVendor'].label = "CaliVendor"
        self.fields['Location'].widget.attrs['readonly'] = True
        self.fields['ProdVendor'].widget.attrs['readonly'] = True
        self.fields['ModuleNo'].widget.attrs['readonly'] = True
        self.fields['CalibratedTicketCreateDate'].initial = datetime.date.today().strftime('%Y-%m-%d')
        self.fields['CalibratedStartTime'].initial = datetime.date.today().strftime('%Y-%m-%d')
        self.fields['ExpectedCalibratedEndTime'].initial = (datetime.date.today() + relativedelta(days=14)).strftime('%Y-%m-%d')

class TransactionRecordForm(forms.ModelForm):
    class Meta:
        model = TransactionRecord
        fields = '__all__'
        exclude = ['Deleted']
        widgets = {
            'TicketCreateTime': DatePickerInput(format='%Y-%m-%d'),
            'TransactionReqTime': DatePickerInput(format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        eqno = kwargs.pop('eqno', None)
        ttno = kwargs.pop('ttno', None)
        photo = kwargs.pop('photo', None)
        description = kwargs.pop('description', None)
        kwargs['initial'] = {'TransactionTicketNo': ttno, 'Description': eqno, 'PhotoLink': photo, 'Description': description}
        super(TransactionRecordForm, self).__init__(*args, **kwargs)
        trans_from = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        trans_to = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        truck_type = [(i['Truck'], i['Truck']) for i in Truck.objects.values('Truck').distinct()]
        self.fields['TransactionTicketNo'].widget.attrs['readonly'] = True
        self.fields['PhotoLink'].widget.attrs['readonly'] = True
        self.fields['TicketCreateUser'].initial = user
        self.fields['TransactionReqUser'].initial = user
        self.fields['TransactionFrom'] = forms.ChoiceField(choices=trans_from)
        self.fields['TransactionTo'] = forms.ChoiceField(choices=trans_to)
        self.fields['TruckType'] = forms.ChoiceField(choices=truck_type)
        self.fields['TransactionFrom'].label = "TransactionFrom"
        self.fields['TransactionTo'].label = "TransactionTo"
        self.fields['TruckType'].label = "TruckType"
        self.fields['TransactionReqTime'].initial = datetime.date.today().strftime('%Y-%m-%d')
        self.fields['TicketCreateTime'].initial = datetime.date.today().strftime('%Y-%m-%d')