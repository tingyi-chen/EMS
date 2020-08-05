from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.http import HttpResponse
from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.core import serializers
from django.middleware.csrf import get_token
from django.core.files.storage import FileSystemStorage
import pandas as pd
import requests
import datetime
import json
import os
from xlrd import XLRDError
from docx import Document
from dateutil.relativedelta import *
from django.forms import formset_factory
from bootstrap_datepicker_plus import DatePickerInput

from .models import EquipmentList, AssetLoanRecord, ToolingCalibrationRecord, NonStockTransactionRecord, TransactionRecord
from .forms import EquipmentForm, AssetLoanRecordForm, ToolingCalibrationRecordForm, NonStockTransactionRecordForm, TransactionRecordForm
'''
Note:
1. views.py:                (1) Define all pages that show to users;
                            (2) Call .html files.
                            (3) Control requests and resonses, finally render to users.
                            (4) Bridge to connect DB.
2. template_name:           Override the default .html file path and name.
3. context_object_name:     Override the default variable that sends to .html files.
4. get_queryset(self):      (1) Default function binding with generic.ListView, and then return "django QuerySet object".
                            (2) Will be executed by django itself.
                            (3) Will be passed to context_object_name.
                            i.e. Model.objects.all() returns all column data in a row.
5. form.cleaned_data['']:   This assignment can catch variables in the post form and then make further usages.
6. form.save():             Save changes to MSSQL DB, this will insert a new row.

Structure:
- Home(generic.View)
- Equipment
    - EquipmentList(generic.ListView)
    - EquipmentForm(generic.edit.FormView)
    - EquipmentDetail(generic.DetailView)
- AssetLoanRecordList(generic.ListView)
    - AssetLoanRecordDetail(generic.DetailView)
- NonStockTransactionList(generic.ListView)
    - NonStockTransactionDetail(generic.DetailView)
- ToolingCalibrationList(generic.ListView)
    = ToolingCalibrationDetail(generic.DetailView)
- FakeLoginAuthList(generic.ListView)
'''

model_list = {
    'equipmentlist': EquipmentList,
    'assetloanrecord': AssetLoanRecord,
    'toolingcalibrationrecord': ToolingCalibrationRecord,
    'nonstocktransactionrecord': NonStockTransactionRecord,
    'transactionrecord': TransactionRecord,
}
form_list = {
    'equipmentlist': EquipmentForm,
    'assetloanrecord': AssetLoanRecordForm,
    'toolingcalibrationrecord': ToolingCalibrationRecordForm,
    'nonstocktransactionrecord': NonStockTransactionRecordForm,
    'transactionrecord': TransactionRecordForm,
}
e_admin_tuple = (
    'emsapp.add_equipmentlist',
    'emsapp.change_equipmentlist',
    'emsapp.delete_equipmentlist',
    'emsapp.view_equipmentlist',
)
a_admin_tuple = (
    'emsapp.add_assetloanrecord',
    'emsapp.change_assetloanrecord',
    'emsapp.delete_assetloanrecord',
    'emsapp.view_assetloanrecord',
)
t_admin_tuple = (
    'emsapp.add_toolingcalibrationrecord',
    'emsapp.change_toolingcalibrationrecord',
    'emsapp.delete_toolingcalibrationrecord',
    'emsapp.view_toolingcalibrationrecord',
)
n_admin_tuple = (
    'emsapp.add_nonstocktransactionrecord',
    'emsapp.change_nonstocktransactionrecord',
    'emsapp.delete_nonstocktransactionrecord',
    'emsapp.view_nonstocktransactionrecord',
)
tr_admin_tuple = (
    'emsapp.add_transactionrecord',
    'emsapp.change_transactionrecord',
    'emsapp.delete_transactionrecord',
    'emsapp.view_transactionrecord',
)
date_dict = {
    '2020':
    {
        'Jul': ['31']
    }
}
value_dict = {
    '2020':
    {
        'Jul': [0]
    }
}
@login_required
@permission_required(e_admin_tuple, raise_exception=True)
def checkbox_validation(request, form, photo_list, redirect_url, render_path, data):
    if len(request.POST.getlist('EquipmentType')) != 3:
        if len(request.POST.getlist('EquipmentType')) != 2:
            if len(request.POST.getlist('EquipmentType')) != 1:
                pass
            elif 'Asset' in request.POST.getlist('EquipmentType'):
                form.fields['AssetNo'].required = True
            elif 'Tool' in request.POST.getlist('EquipmentType'):
                form.fields['ToolingNo'].required = True
                form.fields['LastCalibratedDate'].required = True
                form.fields['NextCalibratedDate'].required = True
            elif 'NonS' in request.POST.getlist('EquipmentType'):
                form.fields['NonStockNo'].required = True
        elif not ('Asset' in request.POST.getlist('EquipmentType')):
            form.fields['LastCalibratedDate'].required = True
            form.fields['NextCalibratedDate'].required = True
            form.fields['NonStockNo'].required = True
        elif not ('Tool' in request.POST.getlist('EquipmentType')):
            form.fields['AssetNo'].required = True
            form.fields['NonStockNo'].required = True
        elif not ('NonS' in request.POST.getlist('EquipmentType')):
            form.fields['AssetNo'].required = True
            form.fields['ToolingNo'].required = True
            form.fields['LastCalibratedDate'].required = True
            form.fields['NextCalibratedDate'].required = True
    else:
        form.fields['EquipmentType'].required = True
        form.fields['AssetNo'].required = True
        form.fields['ToolingNo'].required = True
        form.fields['LastCalibratedDate'].required = True
        form.fields['NextCalibratedDate'].required = True
        form.fields['NonStockNo'].required = True
    if form.is_valid():
        instance = form.save(commit=False)
        instance.EquipmentType = ";".join(request.POST.getlist('EquipmentType'))
        for photo in request.FILES.getlist('PhotoLink'):
            photo_list.append(photo.name)
            instance.PhotoLink = photo
            instance.save()
        photo_str = ";".join(photo_list)
        instance.PhotoLink = photo_str
        instance.save()
        return redirect(redirect_url)
    else:
        return render(request, render_path, data)

@login_required
@permission_required((e_admin_tuple, a_admin_tuple, t_admin_tuple, n_admin_tuple), raise_exception=True)
def update(request, pk):
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    render_path = 'emsapp/' + request.path.split('/')[2] + '/' + request.path.split('/')[2] + 'Update.html'
    permission = 'change_' + request.path.split('/')[2]
    model = model_list[request.path.split('/')[2]]
    model_form = form_list[request.path.split('/')[2]]

    if request.user.has_perm(permission):
        if model == EquipmentList:
            orig_data = model.objects.filter(CountIndex=pk).values()[0]
            instance = get_object_or_404(model, CountIndex=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                form_eqno=orig_data['EquipmentNo'],
                user=orig_data['CreateUser'],
                date=orig_data['CreateDate'],
                update=True
            )
            action = checkbox_validation(request, form, orig_data['PhotoLink'].split(';'), redirect_url, render_path, {'equipment_list': EquipmentList.objects.filter(~Q(Deleted=True)).all(), 'form': form, 'photos': orig_data['PhotoLink'].split(';')})
            return action
        elif model == ToolingCalibrationRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                form_eqno=orig_data['EquipmentNo'],
                form_tcno=orig_data['CalibratedTicketNo'],
                form_tlno=orig_data['ToolingNo'],
                form_name=orig_data['Name'],
                form_en_name=orig_data['EnName'],
                form_mdno=orig_data['ModuleNo'],
                photo=orig_data['PhotoLink'],
                pr_vendor=orig_data['ProdVendor']
            )
            name_prefix = request.path.split('/')[2].replace('record', '')
            return render(request, render_path, {name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(), 'form': form})
        elif model == NonStockTransactionRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                form_eqno=orig_data['EquipmentNo'],
                form_ntno=orig_data['NonStockTicketNo'],
            )
            name_prefix = request.path.split('/')[2].replace('record', '')
            return render(request, render_path, {name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(), 'form': form})
        elif model == AssetLoanRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                form_eqno=orig_data['EquipmentNo'],
                form_atno=orig_data['AssetLoanTicketNo'],
                form_asno=orig_data['AssetNo'],
                photo=orig_data['PhotoLink']
            )
            name_prefix = request.path.split('/')[2].replace('record', '')
            return render(request, render_path, {name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(), 'form': form})
        elif model == TransactionRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                form_eqno=orig_data['EquipmentNo'],
                form_ntno=orig_data['TransactionTicketNo'],
            )
            name_prefix = request.path.split('/')[2].replace('record', '')
            return render(request, render_path, {name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(), 'form': form})
    else:
        print('You are not allowed to do so.')
        return redirect(redirect_url)

@login_required
@permission_required((e_admin_tuple, a_admin_tuple, t_admin_tuple, n_admin_tuple), raise_exception=True)
def delete(request, pk):
    '''
    Note
    (1) Here's a hidden self.user parameter which contains user info
    '''
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    permission = 'delete_' + request.path.split('/')[2]
    model = model_list[request.path.split('/')[2]]

    if request.user.has_perm(permission):
        if model == EquipmentList:
            obj = model.objects.filter(CountIndex=pk)
        else:
            obj = model.objects.filter(TicketNo=pk)
        obj.update(Deleted=True)
        return redirect(redirect_url)
    else:
        print('You are not allowed to do so.')
        return redirect(redirect_url)

@login_required
@permission_required((e_admin_tuple, a_admin_tuple, t_admin_tuple, n_admin_tuple), raise_exception=True)
def create_form(request, *args, **kwargs):
    model = model_list[request.path.split('/')[2]]
    if model == ToolingCalibrationRecord:
        eqpk = args[0]
        t_obj = model.objects
        if t_obj.all() and t_obj.filter(CalibratedTicketNo__icontains='T'):
            pk = str(t_obj.filter(CalibratedTicketNo__icontains='T').latest('TicketNo'))
            latest_tcno = t_obj.filter(TicketNo=pk).values()[0]['CalibratedTicketNo']
            latest_tcno_prefix = latest_tcno.split('_')[0]
            latest_tcno_suffix = latest_tcno.split('_')[1]
            form_tcno = latest_tcno_prefix + '_' + format(int(latest_tcno_suffix) + 1, '06d')
        elif t_obj.all():
            pk = int(str(t_obj.latest('TicketNo')))
            form_tcno = 'T_' + format(pk + 1, '06d')
        else:
            form_tcno = 'T_' + format(1, '06d')
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        form_eqno = e_obj['EquipmentNo']
        form_tlno = e_obj['ToolingNo']
        form_name = e_obj['Name']
        form_en_name = e_obj['EnName']
        photo = e_obj['PhotoLink']
        location = e_obj['Location']
        pr_vendor = e_obj['ProdVendor']
        last_due_date = e_obj['LastCalibratedDate']
        next_due_date = e_obj['NextCalibratedDate']
        form = ToolingCalibrationRecordForm(user=request.user, form_tcno=form_tcno, form_eqno=form_eqno, form_tlno=form_tlno, form_name=form_name, form_en_name=form_en_name, photo=photo, pr_vendor=pr_vendor, location=location, last_due_date=last_due_date, next_due_date=next_due_date)
        return form
    elif model == EquipmentList:
        e_obj = model.objects
        if e_obj.all() and e_obj.filter(EquipmentNo__icontains='E'):
            pk = str(e_obj.filter(EquipmentNo__icontains='E').latest('CountIndex'))
            latest_eqno = e_obj.filter(CountIndex=pk).values()[0]['EquipmentNo']
            latest_eqno_prefix = latest_eqno.split('_')[0]
            latest_eqno_suffix = latest_eqno.split('_')[1]
            form_eqno = latest_eqno_prefix + '_' + format(int(latest_eqno_suffix) + 1, '06d')
        elif e_obj.all():
            pk = int(str(e_obj.latest('CountIndex')))
            form_eqno = 'E_' + format(pk + 1, '06d')
        else:
            form_eqno = 'E_' + format(1, '06d')
        form = EquipmentForm(user=request.user, form_eqno=form_eqno)
        return form
    elif model == NonStockTransactionRecord:
        eqpk = args[0]
        ns_obj = model.objects
        if ns_obj.all() and ns_obj.filter(NonStockTicketNo__icontains='N'):
            pk = str(ns_obj.filter(NonStockTicketNo__icontains='N').latest('TicketNo'))
            latest_ntno = ns_obj.filter(TicketNo=pk).values()[0]['NonStockTicketNo']
            latest_ntno_prefix = latest_ntno.split('_')[0]
            latest_ntno_suffix = latest_ntno.split('_')[1]
            form_ntno = latest_ntno_prefix + '_' + format(int(latest_ntno_suffix) + 1, '06d')
        elif ns_obj.all():
            pk = int(str(ns_obj.latest('TicketNo')))
            form_ntno = 'N_' + format(pk + 1, '06d')
        else:
            form_ntno = 'N_' + format(1, '06d')
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        form_eqno = e_obj['EquipmentNo']
        form = NonStockTransactionRecordForm(user=request.user, form_ntno=form_ntno, form_eqno=form_eqno)
        return form
    elif model == TransactionRecord:
        tr_obj = model.objects
        if tr_obj.all() and tr_obj.filter(TransactionTicketNo__icontains='TR'):
            pk = str(tr_obj.filter(TransactionTicketNo__icontains='TR').latest('TicketNo'))
            latest_ttno = tr_obj.filter(TicketNo=pk).values()[0]['TransactionTicketNo']
            latest_ttno_prefix = latest_ttno.split('_')[0]
            latest_ttno_suffix = latest_ttno.split('_')[1]
            form_ttno = latest_ttno_prefix + '_' + format(int(latest_ttno_suffix) + 1, '06d')
        elif tr_obj.all():
            pk = int(str(tr_obj.latest('TicketNo')))
            form_ttno = 'TR_' + format(pk + 1, '06d')
        else:
            form_ttno = 'TR_' + format(1, '06d')
        form = TransactionRecordForm(user=request.user, form_ttno=form_ttno)
        return form
    elif model == AssetLoanRecord:
        eqpk = args[0]
        a_obj = AssetLoanRecord.objects
        if a_obj.all() and a_obj.filter(AssetLoanTicketNo__icontains='A'):
            pk = str(a_obj.filter(AssetLoanTicketNo__icontains='A').latest('TicketNo'))
            latest_atno = a_obj.filter(TicketNo=pk).values()[0]['AssetLoanTicketNo']
            latest_atno_prefix = latest_atno.split('_')[0]
            latest_atno_suffix = latest_atno.split('_')[1]
            form_atno = latest_atno_prefix + '_' + format(int(latest_atno_suffix) + 1, '06d')
        elif a_obj.all():
            pk = int(str(a_obj.latest('TicketNo')))
            form_atno = 'A_' + format(pk + 1, '06d')
        else:
            form_atno = 'A_' + format(1, '06d')
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        form_eqno = e_obj['EquipmentNo']
        form_asno = e_obj['AssetNo']
        photo = e_obj['PhotoLink']
        form = AssetLoanRecordForm(user=request.user, form_atno=form_atno, form_eqno=form_eqno, form_asno=form_asno, photo=photo)
        return form

@permission_required((
    'emsapp.view_equipmentlist',
    'emsapp.view_assetloanrecord',
    'emsapp.view_toolingcalibrationrecord',
    'emsapp.view_nonstocktransactionrecord'
    ),
    login_url='/emsapp/accounts/login/')
def search(request):
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    render_path = 'emsapp/' + request.path.split('/')[2] + '/' + request.path.split('/')[2] + 'Search.html'
    get_name = request.path.split('/')[2] + '_search'
    model = model_list[request.path.split('/')[2]]

    if model == EquipmentList:
        qs = model.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = model.objects.filter(~Q(Deleted=True)).filter(
                Q(AssetNo__icontains=request.GET.get('assetNo')) & 
                Q(ToolingNo__icontains=request.GET.get('toolNo')) & 
                Q(NonStockNo__icontains=request.GET.get('nonStockNo')) & 
                Q(EquipmentOwnerName__icontains=request.GET.get('ownerName')) &
                Q(Name__icontains=request.GET.get('eqName')) &
                Q(Location__icontains=request.GET.get('location')) &
                Q(Site__icontains=request.GET.get('site')) &
                Q(Status__icontains=request.GET.get('status')) &
                Q(EquipmentType__icontains=request.GET.get('type'))
            )
            return qs
    elif model == AssetLoanRecord:
        qs = model.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = model.objects.filter(~Q(Deleted=True)).filter(
                Q(AssetNo__icontains=request.GET.get('assetNo')) & 
                Q(LoanVendor__icontains=request.GET.get('loanVendor')) &
                Q(Location__icontains=request.GET.get('location'))
            )
            return qs
    elif model == ToolingCalibrationRecord:
        qs = model.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = model.objects.filter(~Q(Deleted=True)).filter(
                Q(ToolingNo__icontains=request.GET.get('toolNo')) & 
                Q(CaliVendor__icontains=request.GET.get('caliVendor')) &
                Q(Name__icontains=request.GET.get('eqName')) &
                Q(Location__icontains=request.GET.get('location'))
            )
            return qs
    elif model == NonStockTransactionRecord:
        qs = model.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = model.objects.filter(~Q(Deleted=True)).filter(
                Q(NonStockNo__icontains=request.GET.get('nonStockNo')) & 
                Q(TransactionFrom__icontains=request.GET.get('transFrom')) &
                Q(TransactionTo__icontains=request.GET.get('transTo')) &
                Q(TruckType__icontains=request.GET.get('truckType')) &
                Q(TransactionReqUser__icontains=request.GET.get('transReqUser'))
            )
            return qs
    elif model == TransactionRecord:
        qs = model.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        print(query_len)
        if query_len != 0:
            qs = model.objects.filter(~Q(Deleted=True)).filter(
                Q(TransactionNo__icontains=request.GET.get('transNo')) & 
                Q(TransactionFrom__icontains=request.GET.get('transFrom')) &
                Q(TransactionTo__icontains=request.GET.get('transTo')) &
                Q(TruckType__icontains=request.GET.get('truckType')) &
                Q(TransactionReqUser__icontains=request.GET.get('transReqUser'))
            )
            return qs

@permission_required((e_admin_tuple, a_admin_tuple, t_admin_tuple, n_admin_tuple), raise_exception=True)
def xlsx_export(request):
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    export_name = request.path.split('/')[2] + '_' + str(datetime.date.today().strftime('%Y_%m_%d')) + '_export.xlsx'
    model = model_list[request.path.split('/')[2]]

    df = pd.DataFrame()
    qs = model.objects.all()
    for q in qs.values():
        df2 = pd.DataFrame.from_dict(q, orient='index').T
        df = pd.concat([df, df2])
    df.to_excel('C:\\Users\\kchen171277\\Desktop\\' + export_name, index=False)
    return redirect(redirect_url)

@permission_required((e_admin_tuple, a_admin_tuple, t_admin_tuple, n_admin_tuple), raise_exception=True)
def xlsx_import(request):
    file_name = request.FILES['import']
    # fs = FileSystemStorage(location='media/import/', base_url='/media/import/')
    fs = FileSystemStorage()
    file_save = fs.save(file_name.name, file_name)
    file_url = fs.url(file_save)
    file_path = os.path.abspath(os.getcwd() + file_url)
    e_obj = EquipmentList.objects

    try:
        df = pd.read_excel(file_path)
        df.fillna('', inplace=True)
        print(df)
        if e_obj.all() and e_obj.filter(EquipmentNo__icontains='E'):
            pk = int(str(e_obj.filter(EquipmentNo__icontains='E').latest('CountIndex')))
            for eqno in range(pk, len(df['CountIndex']) + pk):
                df['CountIndex'].iloc[eqno-pk] = eqno + 1
                df['EquipmentNo'].iloc[eqno-pk] = 'E_' + format(eqno + 1, '06d')
        elif e_obj.all():
            pk = int(str(EquipmentList.objects.latest('CountIndex')))
            for eqno in range(pk, len(df['CountIndex']) + pk):
                df['CountIndex'].iloc[eqno-pk] = eqno + 1
                df['EquipmentNo'].iloc[eqno-pk] = 'E_' + format(eqno + 1, '06d')
        else:
            for eqno in range(0, len(df['CountIndex'])):
                df['CountIndex'].iloc[eqno] = eqno + 1
                df['EquipmentNo'].iloc[eqno] = 'E_' + format(eqno + 1, '06d')
        for k in df.itertuples():
            eqlist = EquipmentList(
                EquipmentNo = k.EquipmentNo,
                EquipmentOwnerID = str(k.EquipmentOwnerID),
                EquipmentOwnerName = k.EquipmentOwnerName,
                AssetNo = str(k.AssetNo),
                ToolingNo = k.ToolingNo,
                NonStockNo = k.NonStockNo,
                EquipmentType = k.EquipmentType,
                EnDescription = k.EnDescription,
                ChDescription = k.ChDescription,
                EquipmentGroup = k.EquipmentGroup,
                Location = k.Location,
                Specification = k.Specification,
                Status = k.Status,
                LastModifyUser = k.LastModifyUser,
                Limitations = k.Limitations,
                SerialNumber = k.SerialNumber,
                CreateUser = k.CreateUser,
                Site = k.Site
                )
            eqlist.save()
    except XLRDError or UnboundLocalError:
        print('Please import .xlsx files')
        print('Import Failed!')
    except FileNotFoundError:
        print('File Not Found! Please check your naming validation, i.e. space')
        print('Import Failed!')
    finally:
        print('Import Success')
        return redirect('/emsapp/equipmentlist')

class ToolCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistCalibrationCheck.html'
    template_name_post = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/calibration/check'
    permission_required = ('emsapp.view_toolingcalibrationrecord', 'emsapp.add_toolingcalibrationrecord', 'emsapp.update_toolingcalibrationrecord', 'emsapp.delete_toolingcalibrationrecord')
    
    def get_data_list(self):
        data_list = []
        tool_list = EquipmentList.objects.filter(EquipmentType__icontains='Tool').filter(~Q(Deleted=True)).values()
        for tool in tool_list:
            next_date = tool['NextCalibratedDate']
            if next_date:
                tool_date_delta = (next_date - datetime.date.today()).days
                if tool_date_delta <= 40:
                    data_list.append({'detail': tool, 'delta': tool_date_delta})
        return data_list

    def get(self, request):
        form = ToolingCalibrationRecordForm()
        data_list = self.get_data_list()
        return render(request, self.template_name, {'data_list': data_list, 'form': form})

    def post(self, request):
        total_count = 0
        error_msg = []
        eq_list = []
        tg_list = []
        data_list = self.get_data_list()
        vd_list = ''.join(request.POST.getlist('CaliVendor')).split()
        lc_list = ''.join(request.POST.getlist('Location')).split()
        acp_list = list(''.join(request.POST.getlist('AvgCalibratedPeriod')))
        for each in request.POST.getlist('EquipmentNo'):
            eq_list.append(each)
            total_count = total_count + 1
            tg_list.append(EquipmentList.objects.filter(EquipmentNo=each).values()[0]['ToolingGroup'])
        tg_list_concat = list(set(tg_list))
        for tg in tg_list_concat:
            eq_count = tg_list.count(tg)
            if (EquipmentList.objects.filter(ToolingGroup=tg).values().count() - eq_count) < EquipmentList.objects.filter(ToolingGroup=tg).values()[0]['LimitFreezeQnty']:
                error_msg.append('Action Denied Due to LF-Qnty of E-Group: ' + tg + ', Freeze: ' + str(EquipmentList.objects.filter(ToolingGroup=tg).values()[0]['LimitFreezeQnty']) + ', Remaining: ' + str(eq_count))
            else:
                pass
        if error_msg:
            form = ToolingCalibrationRecordForm()
            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
        else:
            document = Document()
            table = document.add_table(rows=total_count, cols=2)
            try:
                hdr_cells = table.rows[0].cells
            except IndexError:
                error_msg.append('Please Select One')
            finally:
                if error_msg:
                    form = ToolingCalibrationRecordForm()
                    return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
                else:
                    hdr_cells[0].text = 'EquipmentNo'
                    hdr_cells[1].text = 'ChDescription'
                    for idx, eqno in enumerate(eq_list):
                        t_obj = ToolingCalibrationRecord.objects
                        if t_obj.all() and t_obj.filter(CalibratedTicketNo__icontains='T'):
                            pk = str(t_obj.filter(CalibratedTicketNo__icontains='T').latest('TicketNo'))
                            latest_tcno = t_obj.filter(TicketNo=pk).values()[0]['CalibratedTicketNo']
                            latest_tcno_prefix = latest_tcno.split('_')[0]
                            latest_tcno_suffix = latest_tcno.split('_')[1]
                            form_tcno = latest_tcno_prefix + '_' + format(int(latest_tcno_suffix) + 1, '06d')
                        elif t_obj.all():
                            pk = int(str(t_obj.latest('TicketNo')))
                            form_tcno = 'T_' + format(pk + 1, '06d')
                        else:
                            form_tcno = 'T_' + format(1, '06d')
                        e_obj = EquipmentList.objects.filter(EquipmentNo=eqno).values()[0]
                        post = request.POST.copy()
                        try:
                            post.update({
                                'CalibratedTicketNo': form_tcno,
                                'EquipmentNo': e_obj['EquipmentNo'],
                                'ToolingNo': e_obj['ToolingNo'],
                                'Name': e_obj['Name'],
                                'EnName': e_obj['EnName'],
                                'ModuleNo': e_obj['ModuleNo'],
                                'PhotoLink': e_obj['PhotoLink'],
                                'UnitPrice': e_obj['Cost'],
                                'CalibratedTicketCreateDate': datetime.date.today().strftime('%Y-%m-%d'),
                                'CalibratedStartTime': datetime.date.today().strftime('%Y-%m-%d'),
                                'CalibratedEndTime': (datetime.date.today() + relativedelta(days=14)).strftime('%Y-%m-%d'),
                                'ProdVendor': e_obj['ProdVendor'],
                                'CaliVendor': vd_list[idx],
                                'Location': 'Others'
                            })
                        except IndexError as e:
                            error_msg.append('Please Fill in Columns for The One Selected')
                        finally:
                            if error_msg:
                                form = ToolingCalibrationRecordForm()
                                return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
                            else:
                                request.POST = post
                                form = ToolingCalibrationRecordForm(request.POST)
                                if form.is_valid():
                                    form.save()
                                    eqno = form.cleaned_data['EquipmentNo']
                                    eq = EquipmentList.objects.get(EquipmentNo=eqno)
                                    eq.Status = 'Cali'
                                    eq.LastCalibratedDate = datetime.date.today().strftime('%Y-%m-%d')
                                    eq.NextCalibratedDate = (datetime.date.today() + relativedelta(years=+1)).strftime('%Y-%m-%d')
                                    eq.PlanCalDate = (datetime.date.today() + relativedelta(years=+1) - relativedelta(months=1)).strftime('%Y-%m-%d')
                                    eq.LastModifyUser = str(request.user)
                                    eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                                    eq.save()
                                    row_cells = table.add_row().cells
                                    row_cells[0].text = eqno
                                    row_cells[1].text = EquipmentList.objects.filter(EquipmentNo=eqno).values()[0]['ChDescription']
                                    document.add_page_break()
                                    document.save('demo.docx')
                                else:
                                    error_msg.append('POST form is invalid; Submission CANCELED')
                                    form = ToolingCalibrationRecordForm()
                                    return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})      
                    return redirect('/emsapp/toolingcalibrationrecord')
                                
            
class AssetCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistAssetCheck.html'
    template_name_post = 'emsapp/assetloanrecord/assetloanrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/asset/check'
    permission_required = ('emsapp.view_assetloanrecord', 'emsapp.add_assetloanrecord', 'emsapp.change_assetloanrecord', 'emsapp.delete_assetloanrecord')
    
    def get_data_list(self):
        data_list = []
        asset_list = EquipmentList.objects.filter(EquipmentType__icontains='Asset').filter(~Q(Deleted=True)).values()
        for asset in asset_list:
            data_list.append({'detail': asset})
        return data_list

    def get(self, request):
        data_list = self.get_data_list()
        form = AssetLoanRecordForm()
        return render(request, self.template_name, {'data_list': data_list, 'form': form})

    def post(self, request):
        total_count = 0
        error_msg = []
        ast_list = []
        data_list = self.get_data_list()
        if request.POST.getlist('EquipmentNo'):
            for idx, each in enumerate(request.POST.getlist('EquipmentNo')):
                print(idx, each)
                a_obj = AssetLoanRecord.objects
                if a_obj.all() and a_obj.filter(AssetLoanTicketNo__icontains='A'):
                    pk = str(a_obj.filter(AssetLoanTicketNo__icontains='A').latest('TicketNo'))
                    latest_atno = a_obj.filter(TicketNo=pk).values()[0]['AssetLoanTicketNo']
                    latest_atno_prefix = latest_atno.split('_')[0]
                    latest_atno_suffix = latest_atno.split('_')[1]
                    form_atno = latest_atno_prefix + '_' + format(int(latest_atno_suffix) + 1, '06d')
                elif a_obj.all():
                    pk = int(str(a_obj.latest('TicketNo')))
                    form_atno = 'A_' + format(pk + 1, '06d')
                else:
                    form_atno = 'A_' + format(1, '06d')
                e_obj = EquipmentList.objects.filter(EquipmentNo=each).values()[0]
                post = request.POST.copy()
                try:
                    post.update({
                        'AssetLoanTicketNo': form_atno,
                        'EquipmentNo': e_obj['EquipmentNo'],
                        'AssetNo': e_obj['AssetNo'],
                        'PhotoLink': e_obj['PhotoLink'],
                        'Location': e_obj['Location'],
                        'LoanVendor': request.POST.getlist('LoanVendor')[idx],
                        'Borrower': request.POST.getlist('Borrower')[idx],
                        'LoanReason': request.POST.getlist('LoanReason')[idx],
                        'LoanStartTime': request.POST.getlist('LoanStartTime')[idx],
                        'LoanEndTime': request.POST.getlist('LoanEndTime')[idx],
                    })
                except IndexError:
                    error_msg.append('Please Fill in Columns for The One Selected')
                finally:
                    if error_msg:
                        form = AssetLoanRecordForm()
                        return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
                    else:
                        request.POST = post
                        form = AssetLoanRecordForm(request.POST)
                        if form.is_valid():
                            form.save()
                            eqno = form.cleaned_data['EquipmentNo']
                            loan_start = form.cleaned_data['LoanStartTime']
                            eq = EquipmentList.objects.get(EquipmentNo=eqno)
                            eq.Status = 'Loaned'
                            eq.LastModifyUser = str(request.user)
                            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                            eq.AssetLoanedReturnDate = datetime.datetime.strptime(str(loan_start), '%Y-%m-%d') + relativedelta(months=6)
                            eq.save()
                        else:
                            # form = AssetLoanRecordForm()
                            error_msg.append('POST form is invalid; Submission CANCELED')
                            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
            return redirect('/emsapp/assetloanrecord')
        else:
            error_msg.append('Please Select One')
            form = AssetLoanRecordForm()
            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})                       

class NonStockCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistNonStockCheck.html'
    template_name_post = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/nonstock/check'
    permission_required = ('emsapp.view_nonstocktransactionrecord', 'emsapp.add_nonstocktransactionrecord', 'emsapp.change_nonstocktransactionrecord', 'emsapp.delete_nonstocktransactionrecord')
    
    def get_data_list(self):
        data_list = []
        nons_list = EquipmentList.objects.filter(~Q(Deleted=True)).values()
        for nons in nons_list:
            data_list.append({'detail': nons})
        return data_list

    def get(self, request):
        data_list = self.get_data_list()
        form = NonStockTransactionRecordForm()
        return render(request, self.template_name, {'data_list': data_list, 'form': form})

    def post(self, request):
        total_count = 0
        error_msg = []
        ns_list = []
        data_list = self.get_data_list()
        if request.POST.getlist('EquipmentNo'):
            for idx, each in enumerate(request.POST.getlist('EquipmentNo')):
                n_obj = NonStockTransactionRecord.objects
                if n_obj.all() and n_obj.filter(NonStockTicketNo__icontains='N'):
                    pk = str(n_obj.filter(NonStockTicketNo__icontains='N').latest('TicketNo'))
                    latest_ntno = n_obj.filter(TicketNo=pk).values()[0]['NonStockTicketNo']
                    latest_ntno_prefix = latest_ntno.split('_')[0]
                    latest_ntno_suffix = latest_ntno.split('_')[1]
                    form_ntno = latest_ntno_prefix + '_' + format(int(latest_ntno_suffix) + 1, '06d')
                elif n_obj.all():
                    pk = int(str(n_obj.latest('TicketNo')))
                    form_ntno = 'N_' + format(pk + 1, '06d')
                else:
                    form_ntno = 'N_' + format(1, '06d')
                e_obj = EquipmentList.objects.filter(EquipmentNo=each).values()[0]
                post = request.POST.copy()
                try:
                    post.update({
                        'NonStockTicketNo': form_ntno,
                        'EquipmentNo': e_obj['EquipmentNo'],
                        'TicketCreateUser': request.user,
                        'TicketCreateTime': datetime.date.today().strftime('%Y-%m-%d'),
                        'NonStockNo': request.POST.getlist('NonStockNo')[idx],
                        'TransactionReqTime': request.POST.getlist('TransactionReqTime')[idx],
                        'TransactionReqUser': request.POST.getlist('TransactionReqUser')[idx],
                        'TransactionFrom': request.POST.getlist('TransactionFrom')[idx],
                        'TransactionTo': request.POST.getlist('TransactionTo')[idx],
                        'TruckType': request.POST.getlist('TruckType')[idx],
                    })
                except IndexError:
                    error_msg.append('Please Fill in Columns for The One Selected')
                finally:
                    if error_msg:
                        form = NonStockTransactionRecordForm()
                        return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
                    else:
                        request.POST = post
                        form = NonStockTransactionRecordForm(request.POST)
                        if form.is_valid():
                            form.save()
                            eq = EquipmentList.objects(EquipmentNo=each)
                            eq.Status = 'Trans'
                            eq.LastModifyUser = str(request.user)
                            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                            eq.LastNonStockShipDate = request.POST.getlist('TransactionReqTime')[idx]
                            eq.NonStockNo = request.POST.getlist('NonStockNo')[idx]
                            eq.Location = request.POST.getlist('TransactionTo')[idx]
                            eq.save()
                        else:
                            form = NonStockTransactionRecordForm()
                            error_msg.append('POST form is invalid; Submission CANCELED')
                            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
            return redirect('/emsapp/nonstocktransactionrecord')
        else:
            error_msg.append('Please Select One')
            form = NonStockTransactionRecordForm()
            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})

class TransCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistTransCheck.html'
    template_name_post = 'emsapp/transactionrecord/transactionrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/trans/check'
    permission_required = ('emsapp.view_transactionrecord', 'emsapp.add_transactionrecord', 'emsapp.change_transactionrecord', 'emsapp.delete_nonstocktransactionrecord')
    
    def get_data_list(self):
        data_list = []
        trans_list = EquipmentList.objects.filter(~Q(Deleted=True)).values()
        for trans in trans_list:
            data_list.append({'detail': trans})
        return data_list

    def get(self, request, count):
        # data_list = self.get_data_list()
        # form = TransactionRecordForm()
        # return render(request, self.template_name, {'data_list': data_list, 'form': form})
        form_list=[]
        if count != str(0):
            TransFormSet = formset_factory(TransactionRecordForm, extra=int(count))
            formset = TransFormSet()
            for idx, form in enumerate(formset):
                tr_obj = TransactionRecord.objects
                if tr_obj.all() and tr_obj.filter(TransactionTicketNo__icontains='TR'):
                    pk = str(tr_obj.filter(TransactionTicketNo__icontains='TR').latest('TicketNo'))
                    latest_ttno = tr_obj.filter(TicketNo=pk).values()[0]['TransactionTicketNo']
                    latest_ttno_prefix = latest_ttno.split('_')[0]
                    latest_ttno_suffix = latest_ttno.split('_')[1]
                    form_ttno = latest_ttno_prefix + '_' + format(int(latest_ttno_suffix) + idx + 1, '06d')
                elif tr_obj.all():
                    pk = int(str(tr_obj.latest('TicketNo')))
                    form_ttno = 'TR_' + format(pk + idx + 1, '06d')
                else:
                    form_ttno = 'TR_' + format(idx + 1, '06d')
                form.fields['TransactionReqTime'].widget = DatePickerInput(format='%Y-%m-%d')
                form_list.append({'form': form, 'form_ttno': form_ttno})
            return render(request, self.template_name, {'form_list': form_list})
        else:
            return render(request, self.template_name)

    def post(self, request, count):
        total_count = 0
        error_msg = []
        tr_list = []
        data_list = self.get_data_list()
        if request.POST.getlist('TransactionTicketNo'):
            for idx, each in enumerate(request.POST.getlist('TransactionTicketNo')):
                post = request.POST.copy()
                post.update({
                    'TransactionTicketNo': each,
                    'TransactionReqUser': request.user,
                    'TicketCreateUser': request.user,
                    'TicketCreateTime': datetime.date.today().strftime('%Y-%m-%d'),
                    'TransactionFrom': request.POST.get('form-' + str(idx) + '-TransactionFrom'),
                    'TransactionTo': request.POST.get('form-' + str(idx) + '-TransactionTo'),
                    'TruckType': request.POST.get('form-' + str(idx) + '-TruckType'),
                    'TransactionReqTime': request.POST.get('form-' + str(idx) + '-TransactionReqTime'),
                    'Description': request.POST.get('form-' + str(idx) + '-Description')
                })
                request.POST = post
                # print(post, request.POST.dict())
                form = TransactionRecordForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    description = form.cleaned_data['Description']
                    if 'E_' in description:
                        pos = description.find('E_')
                        eqno = description[pos: pos+8]
                        eq = EquipmentList.objects.get(EquipmentNo=eqno)
                        eq.Status = 'Trans'
                        eq.LastModifyUser = str(request.user)
                        eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                        eq.LastTransactionDate = request.POST.getlist('TransactionReqTime')[idx]
                        eq.Location = request.POST.getlist('TransactionTo')[idx]
                        eq.TransactionTicketNo = each
                        eq.save()
                else:
                    form = TransactionRecordForm()
                    error_msg.append('POST form is invalid; Submission CANCELED')
                    return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
            return redirect('/emsapp/transactionrecord')
        else:
            error_msg.append('Please Select One')
            form = TransactionRecordForm()
            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})

class HomeView(PermissionRequiredMixin, generic.View):
    permission_required = ('emsapp.view_equipmentlist', 'emsapp.view_assetloanrecord', 'emsapp.view_toolingcalibrationrecord', 'emsapp.view_nonstocktransactionrecord')

    def asset(self):
        a_amount = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').all().count()
        a_TMC1 = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').filter(Location='TMC-1').count()
        a_TMC2 = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').filter(Location='TMC-2').count()
        a_others = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').filter((~Q(Location='TMC-1')&~Q(Location='TMC-2'))).count()
        
        year = datetime.date.today().strftime('%Y-%b-%d').split('-')[0]
        month = datetime.date.today().strftime('%Y-%b-%d').split('-')[1]
        day = (datetime.date.today()+relativedelta(days=-1)).strftime('%Y-%b-%d').split('-')[2]
        print(date_dict)
        print(value_dict)
        if year not in date_dict:
            print('1')
            date_dict[year] = {month: [day]}
            value_dict[year] = {month: [a_amount-a_others]}
        elif month not in date_dict[year]:
            print('2')
            date_dict[year][month] = [day]
            value_dict[year][month] = [a_amount-a_others]
        elif day not in date_dict[year][month]:
            print('3')
            date_dict[year][month].append(day)
            value_dict[year][month].append(a_amount-a_others)
        else:
            print('123')
            pass
        labels = {
            'Location': ['TMC-1', 'TMC-2', 'others'],
            'a_lineX': date_dict['2020']['Aug'],
        }
        data = {
            'a_amount': a_amount,
            'a_location': [a_TMC1, a_TMC2, a_others],
            'a_lineY': value_dict['2020']['Aug'],
            'Asset': [],
        }

        asset_list = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').values()

        for asset in asset_list:
            return_date = asset['AssetLoanedReturnDate']
            if return_date:
                asset_date_delta = (return_date - datetime.date.today()).days
                if 20 < asset_date_delta <= 30:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})
                elif 10 < asset_date_delta <= 20:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})
                elif 0 <= asset_date_delta <= 10:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})
                elif asset_date_delta < 0:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})
                else:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})

        return render(self, 'emsapp/overview/asset.html', {'labels': labels, 'data': data,})

    def tool(self):
        t_amount = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Tool').all().count()
        t_TMC1 = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Tool').filter(Location='TMC-1').count()
        t_TMC2 = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Tool').filter(Location='TMC-2').count()
        t_others = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Tool').filter((~Q(Location='TMC-1')&~Q(Location='TMC-2'))).count()

        labels = {
            'Location': ['TMC-1', 'TMC-2', 'others'],
        }
        data = {
            't_amount': t_amount,
            't_location': [t_TMC1, t_TMC2, t_others],
            'Tool': [],
        }

        tool_list = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Tool').values()
        for tool in tool_list:
            next_date = tool['NextCalibratedDate']
            if next_date:
                tool_date_delta = (next_date - datetime.date.today()).days
                if 20 < tool_date_delta <= 30:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
                elif 10 < tool_date_delta <= 20:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
                elif 0 <= tool_date_delta <= 10:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
                elif tool_date_delta < 0:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
                else:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
        
        return render(self, 'emsapp/overview/tool.html', {'labels': labels, 'data': data,})

    def nonstock(self):
        n_amount = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='NonS').all().count()
        n_TMC1 = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='NonS').filter(Location='TMC-1').count()
        n_TMC2 = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='NonS').filter(Location='TMC-2').count()
        n_others = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='NonS').filter((~Q(Location='TMC-1')&~Q(Location='TMC-2'))).count()
        labels = {
            'Location': ['TMC-1', 'TMC-2', 'others'],
        }
        data = {
            'n_amount': n_amount,
            'n_location': [n_TMC1, n_TMC2, n_others],
            'NonStock': [],
        }
        
        return render(self, 'emsapp/overview/nonstock.html', {'labels': labels, 'data': data,})

    def others(self):
        o_obj = EquipmentList.objects.filter(~Q(Deleted=True)).filter(~(Q(EquipmentType__icontains='Asset')|Q(EquipmentType__icontains='Tool')|Q(EquipmentType__icontains='NonS')))
        o_amount = o_obj.all().count()
        o_TMC1 = o_obj.filter(Location='TMC-1').count()
        o_TMC2 = o_obj.filter(Location='TMC-2').count()
        o_others = o_obj.filter((~Q(Location='TMC-1')&~Q(Location='TMC-2'))).count()
        labels = {
            'Location': ['TMC-1', 'TMC-2', 'others'],
        }
        data = {
            'o_nmount': o_amount,
            'o_location': [o_TMC1, o_TMC2, o_others],
            'NonStock': [],
        }

        return render(self, 'emsapp/overview/others.html', {'labels': labels, 'data': data,})

class LoginView(LoginView):
    template_name = 'emsapp/registration/login.html'

class LogoutView(LogoutView):
    template_name = 'emsapp/registration/logout.html'

class ProfileView(LoginRequiredMixin, generic.ListView):
    template_name = 'emsapp/profile.html'
    login_url = '/emsapp/accounts/login/'

    def get_queryset(self):
        return HttpResponse('Profile')

class TrashBinView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('emsapp.view_equipmentlist', 'emsapp.view_assetloanrecord', 'emsapp.view_toolingcalibrationrecord', 'emsapp.view_nonstocktransactionrecord')

    def asset(self):
        a_deleted = AssetLoanRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/asset.html', {'assetloan_record': a_deleted})

    def tool(self):
        t_deleted = ToolingCalibrationRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/tool.html', {'toolingcalibration_record': t_deleted})

    def nonstock(self):
        n_deleted = NonStockTransactionRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/nonstock.html', {'nonstocktransaction_record': n_deleted})

    def equipment(self):
        e_deleted = EquipmentList.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/equipment.html', {'equipment_list': e_deleted})

class EquipmentFormView(PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistMain.html'
    # login_url = '/emsapp/accounts/login/'
    # redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = 'emsapp.view_equipmentlist'
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))

    def search(self):
        if self.user.has_perm(e_admin_tuple):
            form = create_form(self)
            qs = search(self)
            if qs:
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'qs': qs, 'form': form})
            elif self.GET.dict():
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'equipment_list': '', 'form': form})
            else:
                return render(self, 'emsapp/equipmentlist/equipmentlistSearch.html', {'equipment_list': EquipmentList.objects.filter(~Q(Deleted=True)), 'form': form})
        else:
            qs = search(self)
            if qs:
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'equipment_list': ''})
            else:
                return render(self, 'emsapp/equipmentlist/equipmentlistSearch.html', {'equipment_list': EquipmentList.objects.filter(~Q(Deleted=True))})
    
    def get(self, request):
        if request.user.has_perm((e_admin_tuple, a_admin_tuple, t_admin_tuple, n_admin_tuple)):
            form = create_form(request)
            return render(request, self.template_name, {'equipment_list': self.e_obj.all(), 'form': form})
        else:
            return render(request, self.template_name, {'equipment_list': self.e_obj.all()})

    def post(self, request):
        if request.user.has_perm(e_admin_tuple):
            photo_list = []
            redirect_url = '/emsapp/equipmentlist/'
            form = EquipmentForm(request.POST, request.FILES)
            data = {'equipment_list': self.e_obj.all(), 'form': form}
            action = checkbox_validation(request, form, photo_list, redirect_url, self.template_name, data)
            return action
        else:
            return render(request, self.template_name, {'equipment_list': self.e_obj.all()})
        
class EquipmentListDetailView(PermissionRequiredMixin, generic.DetailView):
    model = EquipmentList
    template_name = 'emsapp/equipmentlist/equipmentlistDetail.html'
    permission_required = 'emsapp.view_equipmentlist'

    def get_context_data(self, **kwargs):
        photo_list = []
        context = super(EquipmentListDetailView, self).get_context_data(**kwargs)
        pk = int(str(context['object']))
        try:
            photo_url = self.model.objects.get(CountIndex=pk).PhotoLink.url
        except ValueError:
            photo_url = '/'
        finally:
            root_url = photo_url.rsplit('/', 1)[0] + '/'
            photo_split = self.model.objects.filter(CountIndex=pk).values()[0]['PhotoLink'].split(';')
            for photo in photo_split:
                photo_list.append(root_url + photo)
            context['PhotoLink'] = photo_list
            return context

class EquipmentListImportView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistImport.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/import/form/'
    permission_required = e_admin_tuple
    def get(self, request):
        return render(request, self.template_name)

''' Asset Loan Record '''

class AssetLoanRecordView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_assetloanrecord'
    template_name = 'emsapp/assetloanrecord/assetloanrecord.html'
    context_object_name = 'assetloan_record'

    def get_queryset(self):
        return AssetLoanRecord.objects.filter(~Q(Deleted=True)).all()

    def search(self):
        qs = search(self)
        if qs:
            return render(self, 'emsapp/assetloanrecord/assetloanrecord.html', {'qs': qs})
        elif self.GET.dict():
            return render(self, 'emsapp/assetloanrecord/assetloanrecord.html', {'assetloan_record': ''})
        else:
            return render(self, 'emsapp/assetloanrecord/assetloanrecordSearch.html', {'assetloan_record': AssetLoanRecord.objects.filter(~Q(Deleted=True))})

class AssetLoanRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/assetloanrecord/assetloanrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = a_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    a_obj = AssetLoanRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, eqpk):
        form = create_form(request, eqpk)
        return render(request, self.template_name, {'equipment_list': self.e_obj.all(), 'assetloan_record': self.a_obj.all(), 'form': form})
        
    def post(self, request, eqpk):
        form = AssetLoanRecordForm(request.POST, request.FILES)
        data = {'assetloan_record': self.a_obj.all(), 'form': form}
        if form.is_valid():
            form.save()
            eqno = form.cleaned_data['EquipmentNo']
            loan_start = form.cleaned_data['LoanStartTime']
            eq = EquipmentList.objects.get(EquipmentNo=eqno)
            eq.Status = 'Loaned'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.AssetLoanedReturnDate = datetime.datetime.strptime(str(loan_start), '%Y-%m-%d') + relativedelta(months=6)
            eq.save()
            return redirect('/emsapp/assetloanrecord')
        else:
            return render(request, self.template_name, data)

class AssetLoanRecordDetailView(PermissionRequiredMixin, generic.DetailView):
    model = AssetLoanRecord
    template_name = 'emsapp/assetloanrecord/assetloanrecordDetail.html'
    permission_required = 'emsapp.view_assetloanrecord'

''' Tooling Calibration Record '''

class ToolingCalibrationRecordView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_toolingcalibrationrecord'
    template_name = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html'
    context_object_name = 'toolingcalibration_record'

    def get_queryset(self):
        return ToolingCalibrationRecord.objects.filter(~Q(Deleted=True)).all()

    def search(self):
        qs = search(self)
        if qs:
            return render(self, 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html', {'qs': qs})
        elif self.GET.dict():
            return render(self, 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html', {'toolingcalibration_record': ''})
        else:
            return render(self, 'emsapp/toolingcalibrationrecord/toolingcalibrationrecordSearch.html', {'toolingcalibration_record': ToolingCalibrationRecord.objects.filter(~Q(Deleted=True))})

class ToolingCalibrationRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = t_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    t_obj = ToolingCalibrationRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, pk):
        form = create_form(request, pk)
        return render(request, self.template_name, {'equipment_list': self.e_obj.all(), 'toolingcalibration_record': self.t_obj.all(), 'form': form})
        
    def post(self, request, pk):
        photo_list = []
        redirect_url = '/emsapp/toolingcalibrationrecord/'
        form = ToolingCalibrationRecordForm(request.POST, request.FILES)
        data = {'toolingcalibration_record': self.t_obj.all(), 'form': form}
        if form.is_valid():
            form.save()
            eqno = form.cleaned_data['EquipmentNo']
            eq = EquipmentList.objects.get(EquipmentNo=eqno)
            eq.Status = 'Cali'
            eq.LastCalibratedDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.NextCalibratedDate = (datetime.date.today() + relativedelta(years=+1)).strftime('%Y-%m-%d')
            eq.PlanCalDate = (datetime.date.today() + relativedelta(years=+1) - relativedelta(months=1)).strftime('%Y-%m-%d')
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.POST.get('c-end-date'):
            tool_item = ToolingCalibrationRecord.objects.get(pk=pk)
            tool_item.CalibratedEndTime = request.POST.get('c-end-date')
            eq = EquipmentList.objects.get(EquipmentNo=eqno)
            eq = EquipmentList.objects.get(EquipmentNo=tool_item.EquipmentNo)
            eq.Status = 'Cali'
            eq.LastCalibratedDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.NextCalibratedDate = (datetime.datetime.strptime(request.POST.get('c-end-date'), '%Y-%m-%d') + relativedelta(years=+1)).strftime('%Y-%m-%d')
            NextCalibratedDate = datetime.datetime.strptime(request.POST.get('c-end-date'), '%Y-%m-%d') + relativedelta(years=+1)
            eq.PlanCalDate = (NextCalibratedDate - relativedelta(months=1)).strftime('%Y-%m-%d')
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            tool_item.save()
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.POST.get('m-start-date'):
            tool_item = ToolingCalibrationRecord.objects.get(pk=pk)
            tool_item.MQStartTime = request.POST.get('m-start-date')
            eq = EquipmentList.objects.get(EquipmentNo=tool_item.EquipmentNo)
            eq.Status = 'MQ'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            tool_item.save()
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.POST.get('m-end-date'):
            tool_item = ToolingCalibrationRecord.objects.get(pk=pk)
            tool_item.MQEndTime = request.POST.get('m-end-date')
            eq = EquipmentList.objects.get(EquipmentNo=tool_item.EquipmentNo)
            eq.Status = 'Active'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            tool_item.save()
            return redirect('/emsapp/toolingcalibrationrecord')
        else:
            return render(request, self.template_name, data)

class ToolingCalibrationRecordDetailView(PermissionRequiredMixin, generic.DetailView):
    model = ToolingCalibrationRecord
    template_name = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecordDetail.html'
    permission_required = 'emsapp.view_toolingcalibrationrecord'

    def get_context_data(self, **kwargs):
        context = super(ToolingCalibrationRecordDetailView, self).get_context_data(**kwargs)
        return context

''' Non Stock Transaction Record '''

class NonStockTransactionRecordView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_nonstocktransactionrecord'
    template_name = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html'
    context_object_name = 'nonstocktransaction_record'

    def get_queryset(self):
        return NonStockTransactionRecord.objects.filter(~Q(Deleted=True)).all()

    def search(self):
        qs = search(self)
        if qs:
            return render(self, 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html', {'qs': qs})
        elif self.GET.dict():
            return render(self, 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html', {'nonstocktransaction_record': ''})
        else:
            return render(self, 'emsapp/nonstocktransactionrecord/nonstocktransactionrecordSearch.html', {'nonstocktransaction_record': NonStockTransactionRecord.objects.filter(~Q(Deleted=True))})

class NonStockTransactionRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = n_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    ns_obj = NonStockTransactionRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, eqpk):
        form = create_form(request, eqpk)
        return render(request, self.template_name, {'equipment_list': self.e_obj.all(), 'nonstocktransaction_record': self.ns_obj.all(), 'form': form})
        
    def post(self, request, eqpk):
        form = NonStockTransactionRecordForm(request.POST, request.FILES)
        data = {'equipment_list': self.e_obj.all(), 'nonstocktransaction_record': self.ns_obj.all(), 'form': form}
        if form.is_valid():
            form.save()
            eqno = form.cleaned_data['EquipmentNo']
            eq = EquipmentList.objects.get(EquipmentNo=eqno)
            eq.Status = 'Trans'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.LastNonStockShipDate = request.POST.getlist('TransactionReqTime')[idx]
            eq.NonStockNo = request.POST.getlist('NonStockNo')[idx]
            eq.Location = request.POST.getlist('TransactionTo')[idx]
            eq.save()
            return redirect('/emsapp/nonstocktransactionrecord')
        else:
            return render(request, self.template_name, data)

class NonStockTransactionRecordDetailView(PermissionRequiredMixin, generic.DetailView):
    model = NonStockTransactionRecord
    template_name = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecordDetail.html'
    permission_required = 'emsapp.view_nonstocktransactionrecord'


''' General Transaction Record '''

class TransactionRecordView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_transactionrecord'
    template_name = 'emsapp/transactionrecord/transactionrecord.html'
    context_object_name = 'transaction_record'

    def get_queryset(self):
        return TransactionRecord.objects.filter(~Q(Deleted=True)).all()

    def search(self):
        qs = search(self)
        if qs:
            return render(self, 'emsapp/transactionrecord/transactionrecord.html', {'qs': qs})
        elif self.GET.dict():
            return render(self, 'emsapp/transactionrecord/transactionrecord.html', {'transaction_record': ''})
        else:
            return render(self, 'emsapp/transactionrecord/transactionrecordSearch.html', {'transaction_record': TransactionRecord.objects.filter(~Q(Deleted=True))})

class TransactionRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/transactionrecord/transactionrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = tr_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    tr_obj = TransactionRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, eqpk):
        form = create_form(request, eqpk)
        return render(request, self.template_name, {'equipment_list': self.e_obj.all(), 'transaction_record': self.tr_obj.all(), 'form': form})
        
    def post(self, request, eqpk):
        form = TransactionRecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            description = form.cleaned_data['Description']
            if 'E_' in description:
                pos = description.find('E_')
                eqno = description[pos: pos+8]
                eq = EquipmentList.objects.get(EquipmentNo=eqno)
                eq.Status = 'Trans'
                eq.LastModifyUser = str(request.user)
                eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                eq.LastTransactionDate = request.POST.getlist('TransactionReqTime')[idx]
                eq.Location = request.POST.getlist('TransactionTo')[idx]
                eq.TransactionTicketNo = each
                eq.save()
            return redirect('/emsapp/transactionrecord')
        else:
            return render(request, self.template_name, {'form': form})

class TransactionRecordDetailView(PermissionRequiredMixin, generic.DetailView):
    model = TransactionRecord
    template_name = 'emsapp/transactionrecord/transactionrecordDetail.html'
    permission_required = 'emsapp.view_transactionrecord'