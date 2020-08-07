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
        form_eqno = kwargs.pop('form_eqno', None)
        date = kwargs.pop('date', None)
        update = kwargs.pop('update', None)
        if update:
            kwargs['initial'] = {'EquipmentNo': form_eqno, 'CreateUser': user, 'CreateDate': date}
        kwargs['initial'] = {'EquipmentNo': form_eqno}
        super(EquipmentForm, self).__init__(*args, **kwargs)
        location = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        prod_vendor = [(i['ProdVendorName'], i['ProdVendorName']) for i in ProdVendor.objects.values('ProdVendorName').distinct()]
        team_group = [(i['TeamGroupName'], i['TeamGroupName']) for i in TeamGroup.objects.values('TeamGroupName').distinct()]
        e_group = [(i['EquipmentGroupName'], i['EquipmentGroupName']) for i in EquipmentGroup.objects.values('EquipmentGroupName').distinct()]
        t_group = [(i['ToolingGroupName'], i['ToolingGroupName']) for i in ToolingGroup.objects.values('ToolingGroupName').distinct()]
        status = [(i['Status'], i['Status']) for i in Status.objects.values('Status').distinct()]
        site = [(i['Site'], i['Site']) for i in Site.objects.values('Site').distinct()]
        size = [(i['Size'], i['Size']) for i in Size.objects.values('Size').distinct()]
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
        form_atno = kwargs.pop('form_atno', None)
        form_eqno = kwargs.pop('form_eqno', None)
        form_asno = kwargs.pop('form_asno', None)
        photo = kwargs.pop('photo', None)
        kwargs['initial'] = {'AssetLoanTicketNo': form_atno, 'EquipmentNo': form_eqno, 'AssetNo': form_asno, 'PhotoLink': photo}
        super(AssetLoanRecordForm, self).__init__(*args, **kwargs)
        location = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        vendor = [(i['LoanVendorName'], i['LoanVendorName']) for i in LoanVendor.objects.values('LoanVendorName').distinct()]
        borrower = [(i['BorrowerName'], i['BorrowerName']) for i in Borrower.objects.values('BorrowerName').distinct()]
        self.fields['EquipmentNo'].widget.attrs['readonly'] = True
        self.fields['AssetLoanTicketNo'].widget.attrs['readonly'] = True
        self.fields['AssetNo'].widget.attrs['readonly'] = True
        self.fields['PhotoLink'].widget = forms.TextInput(attrs={'readonly': True, 'required': False})
        self.fields['Location'] = forms.ChoiceField(choices=location)
        self.fields['Borrower'] = forms.ChoiceField(choices=borrower)
        self.fields['LoanVendor'] = forms.ChoiceField(choices=vendor)

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
        form_ntno = kwargs.pop('form_ntno', None)
        form_eqno = kwargs.pop('form_eqno', None)
        kwargs['initial'] = {'NonStockTicketNo': form_ntno, 'EquipmentNo': form_eqno}
        super(NonStockTransactionRecordForm, self).__init__(*args, **kwargs)
        trans_from = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        trans_to = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        truck_type = [(i['Truck'], i['Truck']) for i in Truck.objects.values('Truck').distinct()]
        self.fields['EquipmentNo'].widget.attrs['readonly'] = True
        self.fields['NonStockTicketNo'].widget.attrs['readonly'] = True
        self.fields['TicketCreateUser'].initial = user
        self.fields['TransactionReqUser'].initial = user
        self.fields['TransactionFrom'] = forms.ChoiceField(choices=trans_from)
        self.fields['TransactionTo'] = forms.ChoiceField(choices=trans_to)
        self.fields['TruckType'] = forms.ChoiceField(choices=truck_type)

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
        form_tcno = kwargs.pop('form_tcno', None)
        form_eqno = kwargs.pop('form_eqno', None)
        form_tlno = kwargs.pop('form_tlno', None)
        form_name = kwargs.pop('form_name', None)
        form_en_name = kwargs.pop('form_en_name', None)
        form_mdno = kwargs.pop('form_mdno', None)
        form_site = kwargs.pop('form_site', None)
        photo = kwargs.pop('photo', None)
        pr_vendor = kwargs.pop('pr_vendor', None)
        location = kwargs.pop('location', None)
        last_due_date = kwargs.pop('last_due_date', None)
        next_due_date = kwargs.pop('next_due_date', None)
        kwargs['initial'] = {'CalibratedTicketNo': form_tcno, 'EquipmentNo': form_eqno, 'ToolingNo': form_tlno, 'Name': form_name, 'EnName': form_en_name, 'ModuleNo': form_mdno, 'PhotoLink': photo, 'form_site': form_site, 'ProdVendor': pr_vendor, 'Location': location, 'LastDueDate': last_due_date, 'NextDueDate': next_due_date}
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

class TransactionRecordForm(forms.ModelForm):
    class Meta:
        model = TransactionRecord
        fields = '__all__'
        exclude = ['Deleted']
        widgets = {
            'TicketCreateDate': DatePickerInput(format='%Y-%m-%d'),
            'TransactionReqTime': DatePickerInput(format='%Y-%m-%d'),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        form_ttno = kwargs.pop('form_ttno', None)
        kwargs['initial'] = {'TransactionTicketNo': form_ttno}
        super(TransactionRecordForm, self).__init__(*args, **kwargs)
        trans_from = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        trans_to = [(i['Location'], i['Location']) for i in Location.objects.values('Location').distinct()]
        truck_type = [(i['Truck'], i['Truck']) for i in Truck.objects.values('Truck').distinct()]
        self.fields['TransactionTicketNo'].widget.attrs['readonly'] = True
        self.fields['TicketCreateUser'].initial = user
        self.fields['TransactionReqUser'].initial = user
        self.fields['TransactionFrom'] = forms.ChoiceField(choices=trans_from)
        self.fields['TransactionTo'] = forms.ChoiceField(choices=trans_to)
        self.fields['TruckType'] = forms.ChoiceField(choices=truck_type)