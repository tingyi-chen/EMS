from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib import auth, messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Max
from django.core import serializers
from django.middleware.csrf import get_token
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.forms import formset_factory
import pandas as pd
import requests
import datetime
import json
import os
from xlrd import XLRDError
from docx import Document
from dateutil.relativedelta import *
from bootstrap_datepicker_plus import DatePickerInput

from .models import EquipmentList, AssetLoanRecord, ToolingCalibrationRecord, NonStockTransactionRecord, TransactionRecord, Location, ActionLog, AssetQnty, ToolQnty, NonStockQnty
from .forms import EquipmentForm, AssetLoanRecordForm, ToolingCalibrationRecordForm, NonStockTransactionRecordForm, TransactionRecordForm

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
all_admin_tuple = (
    'emsapp.add_equipmentlist',
    'emsapp.change_equipmentlist',
    'emsapp.delete_equipmentlist',
    'emsapp.view_equipmentlist',
    'emsapp.add_assetloanrecord',
    'emsapp.change_assetloanrecord',
    'emsapp.delete_assetloanrecord',
    'emsapp.view_assetloanrecord',
    'emsapp.add_toolingcalibrationrecord',
    'emsapp.change_toolingcalibrationrecord',
    'emsapp.delete_toolingcalibrationrecord',
    'emsapp.view_toolingcalibrationrecord',
    'emsapp.add_nonstocktransactionrecord',
    'emsapp.change_nonstocktransactionrecord',
    'emsapp.delete_nonstocktransactionrecord',
    'emsapp.view_nonstocktransactionrecord',
    'emsapp.add_transactionrecord',
    'emsapp.change_transactionrecord',
    'emsapp.delete_transactionrecord',
    'emsapp.view_transactionrecord',
)

def make_log(request, action):
    user = request.user
    record = ActionLog(
        User=user,
        Action=action,
        Date=datetime.date.today().strftime('%Y-%m-%d'),
        Time=datetime.datetime.now().time().strftime('%H:%M:%S')
    )
    record.save()

@login_required
@permission_required(e_admin_tuple, raise_exception=True)
def create_validation(request, form, photo_list, redirect_url, render_path, data):
    if len(request.POST.getlist('EquipmentType')) != 3:
        if len(request.POST.getlist('EquipmentType')) != 2:
            if len(request.POST.getlist('EquipmentType')) != 1:
                pass
            elif 'Asset' in request.POST.getlist('EquipmentType'):
                form.fields['AssetNo'].required = True
                return False
            elif 'Tool' in request.POST.getlist('EquipmentType'):
                form.fields['ToolingNo'].required = True
                form.fields['LastCalibratedDate'].required = True
                form.fields['NextCalibratedDate'].required = True
                return True
            elif 'NonS' in request.POST.getlist('EquipmentType'):
                form.fields['NonStockNo'].required = True
                return False
        elif not ('Asset' in request.POST.getlist('EquipmentType')):
            form.fields['ToolingNo'].required = True
            form.fields['LastCalibratedDate'].required = True
            form.fields['NextCalibratedDate'].required = True
            form.fields['NonStockNo'].required = True
            return True
        elif not ('Tool' in request.POST.getlist('EquipmentType')):
            form.fields['AssetNo'].required = True
            form.fields['NonStockNo'].required = True
            return False
        elif not ('NonS' in request.POST.getlist('EquipmentType')):
            form.fields['AssetNo'].required = True
            form.fields['ToolingNo'].required = True
            form.fields['LastCalibratedDate'].required = True
            form.fields['NextCalibratedDate'].required = True
            return True
    else:
        form.fields['EquipmentType'].required = True
        form.fields['AssetNo'].required = True
        form.fields['ToolingNo'].required = True
        form.fields['LastCalibratedDate'].required = True
        form.fields['NextCalibratedDate'].required = True
        form.fields['NonStockNo'].required = True
        return True

@login_required
@permission_required(all_admin_tuple, raise_exception=True)
def update(request, pk):
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    render_path = 'emsapp/' + request.path.split('/')[2] + '/' + request.path.split('/')[2] + 'Update.html'
    permission = 'emsapp.change_' + request.path.split('/')[2]
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
                eqno=orig_data['EquipmentNo'],
                user=orig_data['CreateUser'],
                date=orig_data['CreateDate'],
                update=True
            )
            photo_list = orig_data['PhotoLink'].split(';')
            data = {
                'equipment_list': model.objects.filter(~Q(Deleted=True)).all(),
                'form': form,
                'photos': photo_list
            }
            create_validation(request, form, photo_list, redirect_url, render_path, data)
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
                action_statement = 'Update EquipmentList with EquipmentNo: ' + orig_data['EquipmentNo']
                make_log(request, action_statement)
                return redirect(redirect_url)
            else:
                return render(request, render_path, data)
        elif model == ToolingCalibrationRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                eqno=orig_data['EquipmentNo'],
                tcno=orig_data['CalibratedTicketNo'],
                tlno=orig_data['ToolingNo'],
                name=orig_data['Name'],
                en_name=orig_data['EnName'],
                mdno=orig_data['ModuleNo'],
                photo=orig_data['PhotoLink'],
                pr_vendor=orig_data['ProdVendor'],
                location=orig_data['Location'],
            )
            if form.is_valid():
                form.save()
                action_statement = 'Update ToolingCalibrationRecord with ToolingNo: ' + orig_data['ToolingNo']
                make_log(request, action_statement)
                return redirect('/emsapp/toolingcalibrationrecord')
            else:
                name_prefix = request.path.split('/')[2].replace('record', '')
                return render(
                    request, 
                    render_path, {
                        name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(),
                        'form': form
                        }
                    )
        elif model == NonStockTransactionRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                eqno=orig_data['EquipmentNo'],
                ntno=orig_data['NonStockTicketNo'],
                nsno=orig_data['NonStockNo'],
                name=orig_data['Name'],
                en_name=orig_data['EnName'],
                nonstock_space=orig_data['NonStockSpace'],
                photo=orig_data['PhotoLink'],
            )
            if form.is_valid():
                form.save()
                action_statement = 'Update NonStockTransactionRecord with NonStockNo: ' + orig_data['NonStockNo']
                make_log(request, action_statement)
                return redirect('/emsapp/nonstocktransactionrecord')
            else:
                name_prefix = request.path.split('/')[2].replace('record', '')
                return render(
                    request,
                    render_path, {
                        name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(),
                        'form': form
                        }
                    )
        elif model == AssetLoanRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                eqno=orig_data['EquipmentNo'],
                atno=orig_data['AssetLoanTicketNo'],
                asno=orig_data['AssetNo'],
                name=orig_data['Name'],
                en_name=orig_data['EnName'],
                photo=orig_data['PhotoLink'],
                location=orig_data['Location'],
            )
            if form.is_valid():
                form.save()
                action_statement = 'Update AssetLoanRecord with AssetNo: ' + orig_data['AssetNo']
                make_log(request, action_statement)
                return redirect('/emsapp/assetloanrecord')
            else:
                name_prefix = request.path.split('/')[2].replace('record', '')
                return render(
                    request,
                    render_path, {
                        name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(),
                        'form': form
                        }
                    )
        elif model == TransactionRecord:
            orig_data = model.objects.filter(TicketNo=pk).values()[0]
            instance = get_object_or_404(model, TicketNo=pk)
            form = model_form(
                request.POST or None,
                request.FILES or None,
                instance=instance,
                user=request.user,
                description=orig_data['Description'],
                ttno=orig_data['TransactionTicketNo'],
                photo=orig_data['PhotoLink'],
            )
            if form.is_valid():
                form.save()
                action_statement = 'Update Transrecord with TransactionTicketNo: ' + orig_data['TransactionTicketNo']
                make_log(request, action_statement)
                return redirect('/emsapp/transactionrecord')
            else:
                name_prefix = request.path.split('/')[2].replace('record', '')
                return render(
                    request,
                    render_path, {
                        name_prefix + '_record': model.objects.filter(~Q(Deleted=True)).all(),
                        'form': form
                        }
                    )

@login_required
@permission_required(all_admin_tuple, raise_exception=True)
def delete(request, pk):
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    model = model_list[request.path.split('/')[2]]
    if model == EquipmentList:
        obj = model.objects.filter(CountIndex=pk)
    else:
        obj = model.objects.filter(TicketNo=pk)
    obj.update(Deleted=True)
    action_statement = 'Delete: ' + str(obj)
    make_log(request, action_statement)
    return redirect(redirect_url)

@login_required
@permission_required(all_admin_tuple, raise_exception=True)
def recovery(request, pk):
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    model = model_list[request.path.split('/')[2]]
    data = model.objects.get(pk=pk)
    data.Deleted = False
    data.save()
    action_statement = 'Recover: ' + str(data)
    make_log(request, action_statement)
    return redirect(redirect_url)

@login_required
@permission_required(all_admin_tuple, raise_exception=True)
def create_form(request, *args, **kwargs):
    model = model_list[request.path.split('/')[2]]
    if model == ToolingCalibrationRecord:
        eqpk = args[0]
        t_obj = model.objects
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        if t_obj.all() and t_obj.filter(CalibratedTicketNo__icontains='T'):
            pk = str(t_obj.filter(CalibratedTicketNo__icontains='T').latest('TicketNo'))
            latest_tcno = t_obj.filter(TicketNo=pk).values()[0]['CalibratedTicketNo']
            latest_tcno_prefix = latest_tcno.split('_')[0]
            latest_tcno_suffix = latest_tcno.split('_')[1]
            tcno = latest_tcno_prefix + '_' + format(int(latest_tcno_suffix) + 1, '06d')
        elif t_obj.all():
            pk = int(str(t_obj.latest('TicketNo')))
            tcno = 'T_' + format(pk + 1, '06d')
        else:
            tcno = 'T_' + format(1, '06d')
        eqno = e_obj['EquipmentNo']
        tlno = e_obj['ToolingNo']
        name = e_obj['Name']
        en_name = e_obj['EnName']
        photo = e_obj['PhotoLink']
        location = e_obj['Location']
        pr_vendor = e_obj['ProdVendor']
        last_due_date = e_obj['LastCalibratedDate']
        next_due_date = e_obj['NextCalibratedDate']
        form = ToolingCalibrationRecordForm(
            user=request.user,
            tcno=tcno,
            eqno=eqno,
            tlno=tlno,
            name=name,
            en_name=en_name,
            photo=photo,
            pr_vendor=pr_vendor,
            location=location,
            last_due_date=last_due_date,
            next_due_date=next_due_date
        )
        return form
    elif model == EquipmentList:
        e_obj = model.objects
        if e_obj.all() and e_obj.filter(EquipmentNo__icontains='E'):
            pk = str(e_obj.filter(EquipmentNo__icontains='E').latest('CountIndex'))
            latest_eqno = e_obj.filter(CountIndex=pk).values()[0]['EquipmentNo']
            latest_eqno_prefix = latest_eqno.split('_')[0]
            latest_eqno_suffix = latest_eqno.split('_')[1]
            eqno = latest_eqno_prefix + '_' + format(int(latest_eqno_suffix) + 1, '06d')
        elif e_obj.all():
            pk = int(str(e_obj.latest('CountIndex')))
            eqno = 'E_' + format(pk + 1, '06d')
        else:
            eqno = 'E_' + format(1, '06d')
        form = EquipmentForm(user=request.user, eqno=eqno)
        return form
    elif model == NonStockTransactionRecord:
        eqpk = args[0]
        ns_obj = model.objects
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        if ns_obj.all() and ns_obj.filter(NonStockTicketNo__icontains='N'):
            pk = str(ns_obj.filter(NonStockTicketNo__icontains='N').latest('TicketNo'))
            latest_ntno = ns_obj.filter(TicketNo=pk).values()[0]['NonStockTicketNo']
            latest_ntno_prefix = latest_ntno.split('_')[0]
            latest_ntno_suffix = latest_ntno.split('_')[1]
            ntno = latest_ntno_prefix + '_' + format(int(latest_ntno_suffix) + 1, '06d')
        elif ns_obj.all():
            pk = int(str(ns_obj.latest('TicketNo')))
            ntno = 'N_' + format(pk + 1, '06d')
        else:
            ntno = 'N_' + format(1, '06d')
        eqno = e_obj['EquipmentNo']
        nonstock_space = e_obj['NonStockSpace']
        nsno = e_obj['NonStockNo']
        photo = e_obj['PhotoLink']
        name = e_obj['Name']
        en_name = e_obj['EnName']
        form = NonStockTransactionRecordForm(
            user=request.user,
            ntno=ntno,
            eqno=eqno,
            nonstock_space=nonstock_space,
            nsno=nsno,
            photo=photo,
            name=name,
            en_name=en_name
        )
        return form
    elif model == TransactionRecord:
        eqpk = args[0]
        tr_obj = model.objects
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        if tr_obj.all() and tr_obj.filter(TransactionTicketNo__icontains='TR'):
            pk = str(tr_obj.filter(TransactionTicketNo__icontains='TR').latest('TicketNo'))
            latest_ttno = tr_obj.filter(TicketNo=pk).values()[0]['TransactionTicketNo']
            latest_ttno_prefix = latest_ttno.split('_')[0]
            latest_ttno_suffix = latest_ttno.split('_')[1]
            ttno = latest_ttno_prefix + '_' + format(int(latest_ttno_suffix) + 1, '06d')
        elif tr_obj.all():
            pk = int(str(tr_obj.latest('TicketNo')))
            ttno = 'TR_' + format(pk + 1, '06d')
        else:
            ttno = 'TR_' + format(1, '06d')
        eqno = e_obj['EquipmentNo']
        photo = e_obj['PhotoLink']
        form = TransactionRecordForm(
            user=request.user,
            ttno=ttno,
            eqno=eqno,
            photo=photo,
        )
        return form
    elif model == AssetLoanRecord:
        eqpk = args[0]
        a_obj = AssetLoanRecord.objects
        e_obj = EquipmentList.objects.filter(CountIndex=eqpk).values()[0]
        if a_obj.all() and a_obj.filter(AssetLoanTicketNo__icontains='A'):
            pk = str(a_obj.filter(AssetLoanTicketNo__icontains='A').latest('TicketNo'))
            latest_atno = a_obj.filter(TicketNo=pk).values()[0]['AssetLoanTicketNo']
            latest_atno_prefix = latest_atno.split('_')[0]
            latest_atno_suffix = latest_atno.split('_')[1]
            atno = latest_atno_prefix + '_' + format(int(latest_atno_suffix) + 1, '06d')
        elif a_obj.all():
            pk = int(str(a_obj.latest('TicketNo')))
            atno = 'A_' + format(pk + 1, '06d')
        else:
            atno = 'A_' + format(1, '06d')
        eqno = e_obj['EquipmentNo']
        asno = e_obj['AssetNo']
        photo = e_obj['PhotoLink']
        location = e_obj['Location']
        name = e_obj['Name']
        en_name = e_obj['EnName']
        form = AssetLoanRecordForm(
            user=request.user,
            atno=atno,
            eqno=eqno,
            asno=asno,
            photo=photo,
            location=location,
            name=name,
            en_name=en_name
        )
        return form

@login_required
@permission_required((
    'emsapp.view_equipmentlist',
    'emsapp.view_assetloanrecord',
    'emsapp.view_toolingcalibrationrecord',
    'emsapp.view_nonstocktransactionrecord'
    ),
    raise_exception=True)
def search(request):
    if request.path.split('/')[3] == 'equipment':
        qs = EquipmentList.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = EquipmentList.objects.filter(Q(Deleted=True)).filter(
                Q(AssetNo__icontains=request.GET.get('assetNo')) & 
                Q(ToolingNo__icontains=request.GET.get('toolNo')) & 
                Q(NonStockNo__icontains=request.GET.get('nonStockNo')) & 
                Q(EquipmentOwnerName__icontains=request.GET.get('ownerName')) &
                Q(Name__icontains=request.GET.get('eqName')) &
                Q(Location__icontains=request.GET.get('location')) &
                Q(Site__icontains=request.GET.get('site')) &
                Q(Status__icontains=request.GET.get('status')) &
                Q(EquipmentType__icontains=request.GET.get('type')) &
                Q(TeamGroup__icontains=request.GET.get('teamGroup')) &
                Q(EquipmentGroup__icontains=request.GET.get('equipmentGroup')) &
                Q(ToolingGroup__icontains=request.GET.get('toolingGroup'))
            )
            return qs
    elif request.path.split('/')[3] == 'asset':
        qs = AssetLoanRecord.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = AssetLoanRecord.objects.filter(~Q(Deleted=True)).filter(
                Q(AssetNo__icontains=request.GET.get('assetNo')) & 
                Q(LoanVendor__icontains=request.GET.get('loanVendor')) &
                Q(Location__icontains=request.GET.get('location'))
            )
            return qs
    elif request.path.split('/')[3] == 'tool':
        qs = ToolingCalibrationRecord.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = ToolingCalibrationRecord.objects.filter(~Q(Deleted=True)).filter(
                Q(ToolingNo__icontains=request.GET.get('toolNo')) & 
                Q(CaliVendor__icontains=request.GET.get('caliVendor')) &
                Q(Name__icontains=request.GET.get('eqName')) &
                Q(Location__icontains=request.GET.get('location'))
            )
            return qs
    elif request.path.split('/')[3] == 'nonstock':
        qs = NonStockTransactionRecord.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = NonStockTransactionRecord.objects.filter(~Q(Deleted=True)).filter(
                Q(NonStockNo__icontains=request.GET.get('nonStockNo')) & 
                Q(TransactionFrom__icontains=request.GET.get('transFrom')) &
                Q(TransactionTo__icontains=request.GET.get('transTo')) &
                Q(TruckType__icontains=request.GET.get('truckType')) &
                Q(TransactionReqUser__icontains=request.GET.get('transReqUser'))
            )
            return qs
    elif request.path.split('/')[3] == 'trans':
        qs = TransactionRecord.objects.all()
        query_len = len(list(filter(None, request.GET.dict().values())))
        if query_len != 0:
            qs = TransactionRecord.objects.filter(~Q(Deleted=True)).filter(
                Q(TransactionNo__icontains=request.GET.get('transNo')) & 
                Q(TransactionFrom__icontains=request.GET.get('transFrom')) &
                Q(TransactionTo__icontains=request.GET.get('transTo')) &
                Q(TruckType__icontains=request.GET.get('truckType')) &
                Q(TransactionReqUser__icontains=request.GET.get('transReqUser'))
            )
            return qs
    else:
        redirect_url = '/emsapp/' + request.path.split('/')[2]
        render_path = 'emsapp/' + request.path.split('/')[2] + '/' + request.path.split('/')[2] + 'Search.html'
        get_name = request.path.split('/')[2] + '_search'
        model = model_list[request.path.split('/')[2]]

        if model == EquipmentList:
            qs = model.objects.all()
            query_len = len(list(filter(None, request.GET.dict().values())))
            if query_len != 0:
                print(request.GET.dict())
                qs = model.objects.filter(~Q(Deleted=True)).filter(
                    Q(AssetNo__icontains=request.GET.get('assetNo')) & 
                    Q(ToolingNo__icontains=request.GET.get('toolNo')) & 
                    Q(NonStockNo__icontains=request.GET.get('nonStockNo')) & 
                    Q(EquipmentOwnerName__icontains=request.GET.get('ownerName')) &
                    Q(EnName__icontains=request.GET.get('enName')) &
                    Q(Location__icontains=request.GET.get('location')) &
                    Q(Site__icontains=request.GET.get('site')) &
                    Q(Status__icontains=request.GET.get('status')) &
                    Q(EquipmentType__icontains=request.GET.get('type')) &
                    Q(TeamGroup__icontains=request.GET.get('teamGroup')) &
                    Q(EquipmentGroup__icontains=request.GET.get('equipmentGroup')) &
                    Q(ToolingGroup__icontains=request.GET.get('toolingGroup'))
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
                    Q(TransactionReqUser__icontains=request.GET.get('transReqUser')) &
                    Q(TransactionReqTime__icontains=request.GET.get('transReqTime'))
                )
                return qs
        elif model == TransactionRecord:
            qs = model.objects.all()
            query_len = len(list(filter(None, request.GET.dict().values())))
            if query_len != 0:
                qs = model.objects.filter(~Q(Deleted=True)).filter(
                    Q(TransactionTicketNo__icontains=request.GET.get('transNo')) &
                    Q(TransactionFrom__icontains=request.GET.get('transFrom')) &
                    Q(TransactionTo__icontains=request.GET.get('transTo')) &
                    Q(TruckType__icontains=request.GET.get('truckType')) &
                    Q(TransactionReqUser__icontains=request.GET.get('transReqUser')) &
                    Q(TransactionReqTime__icontains=request.GET.get('transReqTime'))
                )
                return qs
                
@login_required
@permission_required(all_admin_tuple, raise_exception=True)
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
    action_statement = 'Export ' + request.path.split('/')[2].upper() + ' to Desktop: ' + export_name
    make_log(request, action_statement)
    return redirect(redirect_url)

@permission_required(all_admin_tuple, raise_exception=True)
def xlsx_import(request):
    file_name = request.FILES['import']
    # fs = FileSystemStorage(location='media/import/', base_url='/media/import/')
    fs = FileSystemStorage()
    file_save = fs.save(file_name.name, file_name)
    file_url = fs.url(file_save)
    file_path = os.path.abspath(os.getcwd() + file_url)
    redirect_url = '/emsapp/' + request.path.split('/')[2]
    try:
        if request.path.split('/')[2] == 'equipmentlist':
            e_obj = EquipmentList.objects
            df = pd.read_excel(file_path)
            df.fillna('', inplace=True)
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
            for index, row in df.iterrows():
                data_dict = row.to_dict()
                eqlist = EquipmentList(**data_dict)
                eqlist.save()
                action_statement = 'Import Data into EquipmentList with: ' + str(data_dict)
                make_log(request, action_statement)
            return redirect('/emsapp/equipmentlist')
        elif request.path.split('/')[2] == 'assetloanrecord':
            a_obj = AssetLoanRecord.objects
            df = pd.read_excel(file_path)
            df.fillna('', inplace=True)
            if a_obj.all() and a_obj.filter(AssetLoanTicketNo__icontains='A'):
                pk = int(str(a_obj.filter(AssetLoanTicketNo__icontains='A').latest('TicketNo')))
                for atno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[atno-pk] = atno + 1
                    df['AssetLoanTicketNo'].iloc[atno-pk] = 'A_' + format(atno + 1, '06d')
            elif a_obj.all():
                pk = int(str(a_obj.latest('TicketNo')))
                for atno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[atno-pk] = atno + 1
                    df['AssetLoanTicketNo'].iloc[atno-pk] = 'A_' + format(atno + 1, '06d')
            else:
                for atno in range(0, len(df['TicketNo'])):
                    df['TicketNo'].iloc[atno-pk] = atno + 1
                    df['AssetLoanTicketNo'].iloc[atno-pk] = 'A_' + format(atno + 1, '06d')
            for index, row in df.iterrows():
                data_dict = row.to_dict()
                alist = AssetLoanRecord(**data_dict)
                alist.save()
                action_statement = 'Import Data into AssetLoanRecord with: ' + str(data_dict)
                make_log(request, action_statement)
            return redirect('/emsapp/assetloanrecord')
        elif request.path.split('/')[2] == 'toolingcalibrationrecord':
            t_obj = ToolingCalibrationRecord.objects
            df = pd.read_excel(file_path)
            df.fillna('', inplace=True)
            if t_obj.all() and t_obj.filter(ToolingCalibrationTicketNo__icontains='T'):
                pk = str(t_obj.filter(ToolingCalibrationTicketNo__icontains='T').latest('TicketNo'))
                for ttno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[ttno-pk] = ttno + 1
                    df['ToolingCalibrationTicketNo'].iloc[ttno-pk] = 'T_' + format(ttno + 1, '06d')
            elif t_obj.all():
                pk = int(str(t_obj.latest('TicketNo')))
                for ttno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[ttno-pk] = ttno + 1
                    df['ToolingCalibrationTicketNo'].iloc[ttno-pk] = 'T_' + format(ttno + 1, '06d')
            else:
                for ttno in range(0, len(df['TicketNo'])):
                    df['TicketNo'].iloc[ttno-pk] = ttno + 1
                    df['ToolingCalibrationTicketNo'].iloc[ttno-pk] = 'T_' + format(ttno + 1, '06d')
            for index, row in df.iterrows():
                data_dict = row.to_dict()
                tlist = ToolingCalibrationRecord(**data_dict)
                tlist.save()
                action_statement = 'Import Data into ToolingCalibrationRecord with: ' + str(data_dict)
                make_log(request, action_statement)
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.path.split('/')[2] == 'nonstocktransactionrecord':
            n_obj = NonStockTransactionRecord.objects
            df = pd.read_excel(file_path)
            df.fillna('', inplace=True)
            if n_obj.all() and n_obj.filter(NonStockTransactionTicketNo__icontains='N'):
                pk = str(n_obj.filter(NonStockTransactionTicketNo__icontains='N').latest('TicketNo'))
                for ntno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[ntno-pk] = ntno + 1
                    df['NonStockTransactionTicketNo'].iloc[ntno-pk] = 'N_' + format(ntno + 1, '06d')
            elif n_obj.all():
                pk = int(str(n_obj.latest('TicketNo')))
                for ntno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[ntno-pk] = ntno + 1
                    df['NonStockTransactionTicketNo'].iloc[ntno-pk] = 'N_' + format(ntno + 1, '06d')
            else:
                for ntno in range(0, len(df['TicketNo'])):
                    df['TicketNo'].iloc[ntno-pk] = ntno + 1
                    df['NonStockTransactionTicketNo'].iloc[ntno-pk] = 'N_' + format(ntno + 1, '06d')
            for index, row in df.iterrows():
                data_dict = row.to_dict()
                nlist = NonStockTransactionRecord(**data_dict)
                nlist.save()
                action_statement = 'Import Data into NonStockTransactionRecord with: ' + str(data_dict)
                make_log(request, action_statement)
            return redirect('/emsapp/nonstocktransactionrecord')
        elif request.path.split('/')[2] == 'transactionrecord':
            tr_obj = TransactionRecord.objects
            df = pd.read_excel(file_path)
            df.fillna('', inplace=True)
            if tr_obj.all() and tr_obj.filter(TransactionTicketNo__icontains='TR'):
                pk = str(tr_obj.filter(TransactionTicketNo__icontains='TR').latest('TicketNo'))
                for trno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[trno-pk] = trno + 1
                    df['TransactionTicketNo'].iloc[trno-pk] = 'TR_' + format(trno + 1, '06d')
            elif tr_obj.all():
                pk = int(str(tr_obj.latest('TicketNo')))
                for trno in range(pk, len(df['TicketNo']) + pk):
                    df['TicketNo'].iloc[trno-pk] = trno + 1
                    df['TransactionTicketNo'].iloc[trno-pk] = 'TR_' + format(trno + 1, '06d')
            else:
                for trno in range(0, len(df['TicketNo'])):
                    df['TicketNo'].iloc[trno-pk] = trno + 1
                    df['TransactionTicketNo'].iloc[trno-pk] = 'TR_' + format(trno + 1, '06d')
            for index, row in df.iterrows():
                data_dict = row.to_dict()
                print(data_dict)
                trlist = TransactionRecord(**data_dict)
                trlist.save()
                action_statement = 'Import Data into TransactionRecord with: ' + str(data_dict)
                make_log(request, action_statement)
            return redirect('/emsapp/transactionrecord')
    except KeyError:
        error_msg = "Please Choose the Right File Where It's Columns match the Model Field Format"
        messages.error(request, error_msg)
        return redirect(redirect_url)
    except XLRDError or UnboundLocalError:
        error_msg = 'Please import .xlsx files.'
        messages.error(request, error_msg)
        return redirect(redirect_url)
    except FileNotFoundError:
        error_msg = 'File Not Found. Please check your naming validation, i.e. space is not allowed'
        messages.error(request, error_msg)
        return redirect(redirect_url)
    except ValidationError:
        error_msg =  '''There are two reasons for unsuccessful import:
            1. Data Column Name does not match the database, may be (1) invalid or (2) lacking.
            2. Date format is invalid.
            Please have a check.'''
        messages.error(request, error_msg)
        return redirect(redirect_url)
    except ValueError as e:
        error_msg = 'Integer/Float fields got string inside. Please change these fields.'
        messages.error(request, error_msg)
        return redirect(redirect_url)

class ToolCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistCalibrationCheck.html'
    template_name_post = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/calibration/check'
    permission_required = t_admin_tuple
    
    def get_data_list(self):
        data_list = []
        tool_list = EquipmentList.objects.filter(EquipmentType__icontains='Tool').filter(Status='Active').filter(~Q(Deleted=True)).values()
        for tool in tool_list:
            next_date = tool['NextCalibratedDate']
            if next_date:
                tool_date_delta = (next_date - datetime.date.today()).days
                if tool_date_delta <= 60:
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
        tg_list_set = list(set(tg_list))
        for tg in tg_list_set:
            max_LFQ = EquipmentList.objects.filter(ToolingGroup=tg).aggregate(Max('LimitFreezeQnty'))
            eq_count = tg_list.count(tg)
            if (EquipmentList.objects.filter(ToolingGroup=tg).filter(Status='Active').filter(~Q(Deleted=True)).values().count() - eq_count) < max_LFQ['LimitFreezeQnty__max']:
                error_msg.append(
                    'Action Denied Due to LF-Qnty of E-Group: ' +
                    tg + ', Freeze: ' + str(EquipmentList.objects.filter(ToolingGroup=tg).values()[0]['LimitFreezeQnty']) +
                    ', Remaining: ' + str(eq_count)
                )
            else:
                pass
        if error_msg:
            form = ToolingCalibrationRecordForm()
            return render(
                request,
                self.template_name, {
                    'data_list': data_list,
                    'error_msg': error_msg,
                    'form': form
                }
            )
        else:
            document = Document()
            table = document.add_table(rows=total_count, cols=2)
            try:
                hdr_cells = table.rows[0].cells
            except IndexError:
                error_msg.append('Please Select What to Submit')
            finally:
                if error_msg:
                    form = ToolingCalibrationRecordForm()
                    return render(
                        request,
                        self.template_name, {
                            'data_list': data_list,
                            'error_msg': error_msg,
                            'form': form
                        }
                    )
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
                            tcno = latest_tcno_prefix + '_' + format(int(latest_tcno_suffix) + 1, '06d')
                        elif t_obj.all():
                            pk = int(str(t_obj.latest('TicketNo')))
                            tcno = 'T_' + format(pk + 1, '06d')
                        else:
                            tcno = 'T_' + format(1, '06d')
                        e_obj = EquipmentList.objects.filter(EquipmentNo=eqno).values()[0]
                        post = request.POST.copy()
                        post.update({
                            'CalibratedTicketNo': tcno,
                            'EquipmentNo': e_obj['EquipmentNo'],
                            'ToolingNo': e_obj['ToolingNo'],
                            'Name': e_obj['Name'],
                            'EnName': e_obj['EnName'],
                            'ModuleNo': e_obj['ModuleNo'],
                            'PhotoLink': e_obj['PhotoLink'],
                            'UnitPrice': e_obj['Cost'],
                            'CalibratedTicketCreateDate': datetime.date.today().strftime('%Y-%m-%d'),
                            'CalibratedStartTime': datetime.date.today().strftime('%Y-%m-%d'),
                            'ExpectedCalibratedEndTime': (datetime.date.today() + relativedelta(days=14)).strftime('%Y-%m-%d'),
                            'LastDueDate': datetime.date.today().strftime('%Y-%m-%d'),
                            'NextDueDate': (datetime.date.today() + relativedelta(years=1)).strftime('%Y-%m-%d'),
                            'ProdVendor': e_obj['ProdVendor'],
                            'CaliVendor': vd_list[idx],
                            'Location': e_obj['Location']
                        })
                        if error_msg:
                            form = ToolingCalibrationRecordForm()
                            return render(
                                request,
                                self.template_name, {
                                    'data_list': data_list,
                                    'error_msg': error_msg,
                                    'form': form
                                }
                            )
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
                                export_name = 'cali_list' + '_' + str(datetime.date.today().strftime('%Y_%m_%d'))
                                document.save('C:\\Users\\kchen171277\\Desktop\\' + export_name)
                                action_statement = 'Create ToolingCalibrationRecord with: ' + str(post.dict())
                                make_log(request, action_statement)
                            else:
                                for key, value in dict(form.errors).items():
                                    error_msg.append(key+ ': ' + value[0])
                                form = ToolingCalibrationRecordForm()
                                return render(
                                    request,
                                    self.template_name, {
                                        'data_list': data_list,
                                        'error_msg': error_msg,
                                        'form': form
                                    }
                                )      
                    return redirect('/emsapp/toolingcalibrationrecord')

class AssetCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistAssetCheck.html'
    template_name_post = 'emsapp/assetloanrecord/assetloanrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/asset/check'
    permission_required = ('emsapp.view_assetloanrecord', 'emsapp.add_assetloanrecord', 'emsapp.change_assetloanrecord', 'emsapp.delete_assetloanrecord')
    
    def get_data_list(self):
        data_list = []
        asset_list = EquipmentList.objects.filter(EquipmentType__icontains='Asset').filter(Status='Active').filter(~Q(Deleted=True)).values()
        for asset in asset_list:
            data_list.append({'detail': asset})
        return data_list

    def get(self, request):
        data_list = self.get_data_list()
        form = AssetLoanRecordForm()
        return render(
            request,
            self.template_name, {
                'data_list': data_list,
                'form': form
            }
        )

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
                    atno = latest_atno_prefix + '_' + format(int(latest_atno_suffix) + 1, '06d')
                elif a_obj.all():
                    pk = int(str(a_obj.latest('TicketNo')))
                    atno = 'A_' + format(pk + 1, '06d')
                else:
                    atno = 'A_' + format(1, '06d')
                e_obj = EquipmentList.objects.filter(EquipmentNo=each).values()[0]
                post = request.POST.copy()
                try:
                    post.update({
                        'AssetLoanTicketNo': atno,
                        'EquipmentNo': e_obj['EquipmentNo'],
                        'AssetNo': e_obj['AssetNo'],
                        'Name': e_obj['Name'],
                        'EnName': e_obj['EnName'],
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
                            loan_end = form.cleaned_data['LoanEndTime']
                            eq = EquipmentList.objects.get(EquipmentNo=eqno)
                            eq.Status = 'Loaned'
                            eq.LastModifyUser = str(request.user)
                            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                            eq.AssetLoanedReturnDate = str(loan_end)
                            eq.save()
                            action_statement = 'Create AssetLoanRecord with: ' + str(post.dict())
                            make_log(request, action_statement)
                        else:
                            
                            for key, value in dict(form.errors).items():
                                error_msg.append(key+ ': ' + value[0])
                            form = AssetLoanRecordForm()
                            return render(
                                request,
                                self.template_name, {
                                    'data_list': data_list,
                                    'error_msg': error_msg,
                                    'form': form
                                }
                            )
            return redirect('/emsapp/assetloanrecord')
        else:
            error_msg.append('Please Select One')
            form = AssetLoanRecordForm()
            return render(
                request,
                self.template_name, {
                    'data_list': data_list,
                    'error_msg': error_msg,
                    'form': form
                }
            )                       

class NonStockCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistNonStockCheck.html'
    template_name_post = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/nonstock/check'
    permission_required = n_admin_tuple
    
    def get_data_list(self):
        data_list = []
        nons_list = EquipmentList.objects.filter(EquipmentType__icontains='NonS').filter(~Q(Deleted=True)).values()
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
                    ntno = latest_ntno_prefix + '_' + format(int(latest_ntno_suffix) + 1, '06d')
                elif n_obj.all():
                    pk = int(str(n_obj.latest('TicketNo')))
                    ntno = 'N_' + format(pk + 1, '06d')
                else:
                    ntno = 'N_' + format(1, '06d')
                e_obj = EquipmentList.objects.filter(EquipmentNo=each).values()[0]
                post = request.POST.copy()
                try:
                    post.update({
                        'NonStockTicketNo': ntno,
                        'EquipmentNo': e_obj['EquipmentNo'],
                        'Name': e_obj['Name'],
                        'EnName': e_obj['EnName'],
                        'TicketCreateUser': request.user,
                        'TicketCreateTime': datetime.date.today().strftime('%Y-%m-%d'),
                        'NonStockNo': e_obj['NonStockNo'],
                        'NonStockSpace': e_obj['NonStockSpace'],
                        'TransactionReqTime': request.POST.getlist('TransactionReqTime')[idx],
                        'TransactionReqUser': request.POST.getlist('TransactionReqUser')[idx],
                        'TransactionFrom': e_obj['Location'],
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
                            eq = EquipmentList.objects.get(EquipmentNo=each)
                            instance = NonStockTransactionRecord.objects.filter(~Q(Deleted=True)).get(NonStockTicketNo=ntno)
                            instance.PhotoLink = eq.PhotoLink
                            instance.save()
                            eq.Status = 'InActive'
                            eq.LastModifyUser = str(request.user)
                            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                            eq.LastNonStockShipDate = request.POST.getlist('TransactionReqTime')[idx]
                            eq.Location = request.POST.getlist('TransactionTo')[idx]
                            eq.save()
                            action_statement = 'Create NonStockTransactionRecord with: ' + str(post.dict())
                            make_log(request, action_statement)
                        else:
                            for key, value in dict(form.errors).items():
                                error_msg.append(key+ ': ' + value[0])
                            form = NonStockTransactionRecordForm()
                            return render(request, self.template_name, {'data_list': data_list, 'error_msg': error_msg, 'form': form})
            return redirect('/emsapp/nonstocktransactionrecord')
        else:
            error_msg.append('Please Select One')
            form = NonStockTransactionRecordForm()
            return render(
                request,
                self.template_name, {
                    'data_list': data_list,
                    'error_msg': error_msg,
                    'form': form
                }
            )

class TransCheckView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistTransCheck.html'
    template_name_post = 'emsapp/transactionrecord/transactionrecord.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/trans/check'
    permission_required = tr_admin_tuple
    
    def get_data_list(self):
        data_list = []
        trans_list = EquipmentList.objects.filter(Status='Active').filter(~Q(Deleted=True)).values()
        for trans in trans_list:
            data_list.append({'detail': trans})
        return data_list

    def get(self, request, count):
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
                    ttno = latest_ttno_prefix + '_' + format(int(latest_ttno_suffix) + idx + 1, '06d')
                elif tr_obj.all():
                    pk = int(str(tr_obj.latest('TicketNo')))
                    ttno = 'TR_' + format(pk + idx + 1, '06d')
                else:
                    ttno = 'TR_' + format(idx + 1, '06d')
                form.fields['TransactionReqTime'].widget = DatePickerInput(format='%Y-%m-%d')
                form_list.append({'form': form, 'ttno': ttno})
            return render(
                request,
                self.template_name, {
                    'form_list': form_list
                }
            )
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
                    'TransactionReqUser': request.POST.get('form-' + str(idx) + '-TransactionReqUser'),
                    'TicketCreateUser': request.user,
                    'TicketCreateTime': datetime.date.today().strftime('%Y-%m-%d'),
                    'TransactionFrom': request.POST.get('form-' + str(idx) + '-TransactionFrom'),
                    'TransactionTo': request.POST.get('form-' + str(idx) + '-TransactionTo'),
                    'TruckType': request.POST.get('form-' + str(idx) + '-TruckType'),
                    'TransactionReqTime': request.POST.get('form-' + str(idx) + '-TransactionReqTime'),
                    'Description': request.POST.get('form-' + str(idx) + '-Description')
                })
                request.POST = post
                form = TransactionRecordForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    description = form.cleaned_data['Description']
                    try:
                        if 'E_' in description:
                            pos = description.find('E_')
                            eqno = description[pos: pos+8]
                            eq = EquipmentList.objects.get(EquipmentNo=eqno)
                            instance = TransactionRecord.objects.filter(~Q(Deleted=True)).get(TransactionTicketNo=each)
                            instance.PhotoLink = eq.PhotoLink
                            instance.save()
                            eq.LastModifyUser = str(request.user)
                            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                            eq.LastTransactionDate = request.POST.getlist('TransactionReqTime')[idx]
                            eq.Location = request.POST.getlist('TransactionTo')[idx]
                            eq.TransactionTicketNo = each
                            eq.save()
                            action_statement = 'Create TransactionRecord with: ' + str(post.dict())
                            make_log(request, action_statement)
                    except ObjectDoesNotExist:
                        error_msg.append('Please input an existed EquipmentNo in the Description')
                        return render(
                            request,
                            self.template_name, {
                                'data_list': data_list,
                                'error_msg': error_msg,
                                'form': form
                            }
                        )
                    return redirect('/emsapp/transactionrecord')
                else:
                    for key, value in dict(form.errors).items():
                        error_msg.append(key+ ': ' + value[0])
                    form = TransactionRecordForm()
                    return render(
                        request,
                        self.template_name, {
                            'data_list': data_list,
                            'error_msg': error_msg,
                            'form': form
                        }
                    )
        else:
            error_msg.append('Please Select One')
            form = TransactionRecordForm()
            return render(
                request,
                self.template_name, {
                    'data_list': data_list,
                    'error_msg': error_msg,
                    'form': form
                }
            )

class HomeView(LoginRequiredMixin, PermissionRequiredMixin, generic.View):
    permission_required = (
        'emsapp.view_equipmentlist',
        'emsapp.view_assetloanrecord',
        'emsapp.view_toolingcalibrationrecord',
        'emsapp.view_nonstocktransactionrecord'
    )
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/home/asset/'

    @login_required
    def asset(self):
        a_amount = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').all().count()
        
        labels = {
            'Location': [],
            'a_lineX': [],
        }
        data = {
            'a_amount': a_amount,
            'a_location': [],
            'a_lineY': [],
            'Asset': [],
        }

        year = datetime.date.today().strftime('%Y-%b-%d').split('-')[0]
        month = datetime.date.today().strftime('%Y-%b-%d').split('-')[1]
        day = (datetime.date.today()+relativedelta(days=-1)).strftime('%Y-%b-%d').split('-')[2]

        latest_qnty = AssetQnty.objects.filter(Year=year).filter(Month=month).filter(Day=day).values()
        if not latest_qnty:
            asset_qnty = AssetQnty(
                Year=year,
                Month=month,
                Day=day,
                Quantity=a_amount
            )
            asset_qnty.save()

        for each in AssetQnty.objects.all().values():
            labels['a_lineX'].append(each['Year']+each['Month']+each['Day'])
            data['a_lineY'].append(int(each['Quantity']))
        # if year not in date_dict['Asset']:
        #     print('1')
        #     date_dict['Asset'][year] = {month: [day]}
        #     value_dict['Asset'][year] = {month: [a_amount]}
        # elif month not in date_dict['Asset'][year]:
        #     print('2')
        #     date_dict['Asset'][year][month] = [day]
        #     value_dict['Asset'][year][month] = [a_amount]
        # elif day not in date_dict['Asset'][year][month]:
        #     print('3')
        #     date_dict['Asset'][year][month].append(day)
        #     value_dict['Asset'][year][month].append(a_amount)
        # else:
        #     print('123')
        #     pass

        asset_list = EquipmentList.objects.filter(EquipmentType__icontains='Asset').filter(~Q(Deleted=True)).order_by('AssetLoanedReturnDate').values()
        for asset in asset_list:
            return_date = asset['AssetLoanedReturnDate']
            if return_date:
                asset_date_delta = (return_date - datetime.date.today()).days
                if asset_date_delta <= 60:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})

        for loc_dict in Location.objects.all().values():
            loc = loc_dict['Location']
            labels['Location'].append(loc)
            data['a_location'].append(EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Asset').filter(Location=loc).count())

        return render(
            self,
            'emsapp/overview/asset.html', {
                'labels': labels,
                'data': data
            }
        )

    @login_required
    def tool(self):
        t_amount = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='Tool').all().count()
        labels = {
            'Location': ['Cali'],
            't_lineX': [],
        }
        data = {
            't_amount': t_amount,
            't_location': [EquipmentList.objects.filter(EquipmentType__icontains='Tool').filter(Q(Status='Cali')|Q(Status='MQ')).count()],
            't_lineY': [],
            'Tool': [],
        }
        year = datetime.date.today().strftime('%Y-%b-%d').split('-')[0]
        month = datetime.date.today().strftime('%Y-%b-%d').split('-')[1]
        day = (datetime.date.today()+relativedelta(days=-1)).strftime('%Y-%b-%d').split('-')[2]
        latest_qnty = ToolQnty.objects.filter(Year=year).filter(Month=month).filter(Day=day).values()
        if not latest_qnty:
            tool_qnty = ToolQnty(
                Year=year,
                Month=month,
                Day=day,
                Quantity=t_amount
            )
            tool_qnty.save()
        for each in ToolQnty.objects.all().values():
            labels['t_lineX'].append(each['Year']+each['Month']+each['Day'])
            data['t_lineY'].append(int(each['Quantity']))
        tool_list = EquipmentList.objects.filter(EquipmentType__icontains='Tool').filter(Status='Active').filter(~Q(Deleted=True)).order_by('NextCalibratedDate').values()
        for tool in tool_list:
            next_date = tool['NextCalibratedDate']
            if next_date:
                tool_date_delta = (next_date - datetime.date.today()).days
                if tool_date_delta <= 60:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
        for loc_dict in Location.objects.all().values():
            loc = loc_dict['Location']
            if loc == 'WH':
                pass
            else:
                labels['Location'].append(loc)
                data['t_location'].append(EquipmentList.objects.filter(EquipmentType__icontains='Tool').filter(Status='Active').filter(~Q(Deleted=True)).filter(Location=loc).count())
        return render(
            self,
            'emsapp/overview/tool.html', {
                'labels': labels,
                'data': data
            }
        )

    @login_required 
    def nonstock(self):
        n_space = 0
        n_amount = EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='NonS').all().count()
        ns_space = EquipmentList.objects.filter(EquipmentType__icontains='NonS').filter(Status__icontains='InActive').filter(~Q(Deleted=True)).values()
        for ns in ns_space:
            space = ns['NonStockSpace']
            if space:
                n_space = n_space + space
        n_space_percent = n_space/500*100
        labels = {
            'Location': [],
            'n_lineX': [],
        }
        data = {
            'n_amount': n_amount,
            'n_location': [],
            'n_lineY': [],
            'NonStock': [],
            'ns_space': n_space_percent,
        }
        year = datetime.date.today().strftime('%Y-%b-%d').split('-')[0]
        month = datetime.date.today().strftime('%Y-%b-%d').split('-')[1]
        day = (datetime.date.today()+relativedelta(days=-1)).strftime('%Y-%b-%d').split('-')[2]
        latest_qnty = NonStockQnty.objects.filter(Year=year).filter(Month=month).filter(Day=day).values()
        if not latest_qnty:
            nons_qnty = NonStockQnty(
                Year=year,
                Month=month,
                Day=day,
                Quantity=n_amount
            )
            nons_qnty.save()
        for each in NonStockQnty.objects.all().values():
            labels['n_lineX'].append(each['Year']+each['Month']+each['Day'])
            data['n_lineY'].append(int(each['Quantity']))
        ns_list = EquipmentList.objects.filter(EquipmentType__icontains='NonS').filter(Status='InActive').filter(~Q(Deleted=True)).order_by('LastNonStockShipDate').values()
        for ns in ns_list:
            date = ns['LastNonStockShipDate']
            if date:
                ns_date_delta = (datetime.date.today() - date).days
                if ns_date_delta >= 180:
                    data['NonStock'].append({'No': ns['NonStockNo'], 'Date': ns_date_delta})

        for loc_dict in Location.objects.all().values():
            loc = loc_dict['Location']
            labels['Location'].append(loc)
            data['n_location'].append(EquipmentList.objects.filter(~Q(Deleted=True)).filter(EquipmentType__icontains='NonS').filter(Location=loc).count())

        return render(
            self,
            'emsapp/overview/nonstock.html', {
                'labels': labels,
                'data': data
            }
        )

    @login_required
    def info(self):
        data = {
            'Asset': [],
            'Tool': [],
            'NonStock': [],
        }
        asset_list = AssetLoanRecord.objects.filter(~Q(Deleted=True)).order_by('LoanEndTime').values()
        for asset in asset_list:
            return_date = asset['LoanEndTime']
            if return_date:
                asset_date_delta = (return_date - datetime.date.today()).days
                if asset_date_delta <= 60:
                    data['Asset'].append(asset)

        tool_list = ToolingCalibrationRecord.objects.filter(~Q(Deleted=True)).order_by('NextDueDate').values()
        for tool in tool_list:
            next_date = tool['NextDueDate']
            if next_date:
                tool_date_delta = (next_date - datetime.date.today()).days
                if tool_date_delta <= 60:
                    data['Tool'].append(tool)

        ns_list = NonStockTransactionRecord.objects.filter(~Q(Deleted=True)).order_by('TransactionReqTime').values()
        for ns in ns_list:
            date = ns['TransactionReqTime']
            if date:
                ns_date_delta = (datetime.date.today() - date).days
                if ns_date_delta <= 180:
                    data['NonStock'].append(ns)

        return render(
            self,
            'emsapp/overview/info.html', {
                'data': data
            }
        )

class LoginView(LoginView):
    template_name = 'emsapp/registration/login.html'

class LogoutView(LogoutView):
    template_name = 'emsapp/registration/logout.html'

class TrashBinView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = ('emsapp.view_equipmentlist', 'emsapp.view_assetloanrecord', 'emsapp.view_toolingcalibrationrecord', 'emsapp.view_nonstocktransactionrecord')
    login_url = '/emsapp/accounts/login/'

    @login_required
    def asset(self):
        a_deleted = AssetLoanRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/asset.html', {'assetloan_record': a_deleted})

    @login_required
    def tool(self):
        t_deleted = ToolingCalibrationRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/tool.html', {'toolingcalibration_record': t_deleted})

    @login_required
    def nonstock(self):
        n_deleted = NonStockTransactionRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/nonstock.html', {'nonstocktransaction_record': n_deleted})

    @login_required
    def equipment(self):
        e_deleted = EquipmentList.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/equipment.html', {'equipment_list': e_deleted})

    @login_required
    def trans(self):
        tr_deleted = TransactionRecord.objects.filter(Q(Deleted=True)).all()
        return render(self, 'emsapp/trashbin/trans.html', {'transaction_record': tr_deleted})

    @login_required
    def search(self):
        qs = search(self)
        if self.path.split('/')[3] == 'equipment':
            if qs:
                return render(self, 'emsapp/trashbin/equipment.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/trashbin/equipment.html', {'equipment_list': ''})
            else:
                return render(
                    self,
                    'emsapp/trashbin/equipmentSearch.html', {
                        'equipment_list': EquipmentList.objects.filter(Q(Deleted=True))
                    }
                )
        elif self.path.split('/')[3] == 'asset':
            if qs:
                return render(self, 'emsapp/trashbin/asset.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/trashbin/asset.html', {'assetloan_record': ''})
            else:
                return render(
                    self,
                    'emsapp/trashbin/assetSearch.html', {
                        'assetloan_record': AssetLoanRecord.objects.filter(Q(Deleted=True))
                    }
                )
        elif self.path.split('/')[3] == 'tool':
            if qs:
                return render(self, 'emsapp/trashbin/tool.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/trashbin/tool.html', {'toolingcalibration_record': ''})
            else:
                return render(
                    self,
                    'emsapp/trashbin/toolSearch.html', {
                        'toolingcalibration_record': ToolingCalibrationRecord.objects.filter(Q(Deleted=True))
                    }
                )
        elif self.path.split('/')[3] == 'nonstock':
            if qs:
                return render(self, 'emsapp/trashbin/nonstock.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/trashbin/nonstock.html', {'nonstocktransaction_record': ''})
            else:
                return render(
                    self,
                    'emsapp/trashbin/nonstockSearch.html', {
                        'nonstocktransaction_record': NonStockTransactionRecord.objects.filter(Q(Deleted=True))
                    }
                )
        elif self.path.split('/')[3] == 'trans':
            if qs:
                return render(self, 'emsapp/trashbin/trans.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/trashbin/trans.html', {'transaction_record': ''})
            else:
                return render(
                    self,
                    'emsapp/trashbin/transSearch.html', {
                        'transaction_record': TransactionRecord.objects.filter(Q(Deleted=True))
                    }
                )

class EquipmentFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    template_name = 'emsapp/equipmentlist/equipmentlistMain.html'
    permission_required = 'emsapp.view_equipmentlist'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/equipmentlist/'
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))

    def search(self):
        if self.user.has_perms(e_admin_tuple):
            form = create_form(self)
            qs = search(self)
            if qs:
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'qs': qs, 'form': form})
            elif self.GET.dict():
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'equipment_list': '', 'form': form})
            else:
                return render(
                    self,
                    'emsapp/equipmentlist/equipmentlistSearch.html', {
                        'equipment_list': EquipmentList.objects.filter(~Q(Deleted=True)),
                        'form': form
                    }
                )
        else:
            qs = search(self)
            if qs:
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'qs': qs})
            elif self.GET.dict():
                return render(self, 'emsapp/equipmentlist/equipmentlistMain.html', {'equipment_list': ''})
            else:
                return render(
                    self,
                    'emsapp/equipmentlist/equipmentlistSearch.html', {
                        'equipment_list': EquipmentList.objects.filter(~Q(Deleted=True))
                    }
                )
    
    def get(self, request):
        if request.user.has_perms(all_admin_tuple):
            form = create_form(request)
            for eq in EquipmentList.objects.all():
                eq_type = eq.EquipmentType.split(';')
                if eq.AssetNo and not 'Asset' in eq_type:
                    eq_type.append('Asset')
                    eq.EquipmentType = ';'.join(eq_type)
                    eq.save()
                elif eq.ToolingNo and not 'Tool' in eq_type:
                    eq_type.append('Tool')
                    eq.EquipmentType = ';'.join(eq_type)
                    eq.save()
                elif eq.NonStockNo and not 'NonS' in eq_type:
                    eq_type.append('NonS')
                    eq.EquipmentType = ';'.join(eq_type)
                    eq.save()
            return render(
                request,
                self.template_name, {
                    'equipment_list': self.e_obj.all(),
                    'form': form
                }
            )
        else:
            return render(request, self.template_name, {'equipment_list': self.e_obj.all()})

    def post(self, request):
        if request.user.has_perms(e_admin_tuple):
            photo_list = []
            redirect_url = '/emsapp/equipmentlist/'
            form = EquipmentForm(request.POST, request.FILES)
            tool_bool = create_validation(request, form, photo_list, redirect_url, self.template_name, {'equipment_list': self.e_obj.all(), 'form': form})
            if form.is_valid():
                instance = form.save(commit=False)
                instance.EquipmentType = ";".join(request.POST.getlist('EquipmentType'))
                instance.NonStockSpace = int(request.POST.get('Length'))*int(request.POST.get('Width'))
                for photo in request.FILES.getlist('PhotoLink'):
                    photo_list.append(photo.name)
                    instance.PhotoLink = photo
                    instance.save()
                photo_str = ";".join(photo_list)
                instance.PhotoLink = photo_str
                instance.save()
                action_statement = 'Create EquipentList with: ' + str(request.POST.dict())
                make_log(request, action_statement)
                return redirect(redirect_url)
            else:
                if tool_bool == True:
                    post = request.POST.copy()
                    post.update({
                        'LastCalibratedDate': datetime.date.today().strftime('%Y-%m-%d'),
                        'NextCalibratedDate': (datetime.date.today()+relativedelta(years=1)).strftime('%Y-%m-%d'),
                    })
                    request.POST = post
                    form = EquipmentForm(request.POST, request.FILES)
                    if form.is_valid:
                        instance = form.save(commit=False)
                        instance.EquipmentType = ";".join(request.POST.getlist('EquipmentType'))
                        instance.NonStockSpace = int(request.POST.get('Length'))*int(request.POST.get('Width'))
                        for photo in request.FILES.getlist('PhotoLink'):
                            photo_list.append(photo.name)
                            instance.PhotoLink = photo
                            instance.save()
                        photo_str = ";".join(photo_list)
                        instance.PhotoLink = photo_str
                        instance.save()
                        action_statement = 'Create EquipentList with: ' + str(request.POST.dict())
                        make_log(request, action_statement)
                        return redirect(redirect_url)
                    else:
                        return render(
                        request,
                        self.template_name, {
                            'equipment_list': self.e_obj.all(),
                            'form': form
                        }
                    )
                return render(
                    request,
                    self.template_name, {
                        'equipment_list': self.e_obj.all(),
                        'form': form
                    }
                )
        else:
            return render(request, self.template_name, {'equipment_list': self.e_obj.all()})
        
class EquipmentListDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = EquipmentList
    template_name = 'emsapp/equipmentlist/equipmentlistDetail.html'
    permission_required = 'emsapp.view_equipmentlist'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/equipmentlist/'

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

''' Asset Loan Record '''

class AssetLoanRecordView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_assetloanrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/assetloanrecord/'
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
            return render(
                self,
                'emsapp/assetloanrecord/assetloanrecordSearch.html', {
                    'assetloan_record': AssetLoanRecord.objects.filter(~Q(Deleted=True))
                }
            )

class AssetLoanRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/assetloanrecord/assetloanrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = a_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    a_obj = AssetLoanRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, pk):
        form = create_form(request, pk)
        return render(
            request,
            self.template_name, {
                'equipment_list': self.e_obj.all(),
                'assetloan_record': self.a_obj.all(),
                'form': form
            }
        )

    def post(self, request, pk):
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
            action_statement = 'Create AssetLoanRecord with: ' + str(request.POST.dict())
            make_log(request, action_statement)
            return redirect('/emsapp/assetloanrecord')
        elif request.POST.get('l-end-time'):
            asset_item = AssetLoanRecord.objects.get(pk=pk)
            asset_item.ActualReturnDate = request.POST.get('l-end-time')
            eq = EquipmentList.objects.get(EquipmentNo=asset_item.EquipmentNo)
            eq.Status = 'Active'
            eq.AssetLoanedReturnDate = request.POST.get('l-end-time')
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            asset_item.save()
            action_statement = (
                'Update Asset Loan End Date with: ' + str(request.POST.get('l-end-time')) + 
                ' for ' + asset_item.EquipmentNo
            )
            make_log(request, action_statement)
            return redirect('/emsapp/assetloanrecord')
        else:
            return render(request, self.template_name, data)

class AssetLoanRecordDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = AssetLoanRecord
    template_name = 'emsapp/assetloanrecord/assetloanrecordDetail.html'
    permission_required = 'emsapp.view_assetloanrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/assetloanrecord/'

    def get_context_data(self, **kwargs):
        photo_list = []
        context = super(AssetLoanRecordDetailView, self).get_context_data(**kwargs)
        pk = int(str(context['object']))
        photo_split = self.model.objects.filter(TicketNo=pk).values()[0]['PhotoLink'].split(';')
        context['PhotoLink'] = photo_split
        return context

''' Tooling Calibration Record '''

class ToolingCalibrationRecordView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_toolingcalibrationrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/toolingcalibrationrecord/'
    template_name = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html'
    context_object_name = 'toolingcalibration_record'

    def get_queryset(self):
        return ToolingCalibrationRecord.objects.filter(~Q(Deleted=True)).all()

    def search(self):
        qs = search(self)
        if qs:
            return render(self, 'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html', {'qs': qs})
        elif self.GET.dict():
            return render(
                self,
                'emsapp/toolingcalibrationrecord/toolingcalibrationrecord.html', {
                    'toolingcalibration_record': ''
                }
            )
        else:
            return render(
                self,
                'emsapp/toolingcalibrationrecord/toolingcalibrationrecordSearch.html', {
                    'toolingcalibration_record': ToolingCalibrationRecord.objects.filter(~Q(Deleted=True))
                }
            )

class ToolingCalibrationRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = t_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    t_obj = ToolingCalibrationRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, pk):
        form = create_form(request, pk)
        return render(
            request,
            self.template_name, {
                'equipment_list': self.e_obj.all(),
                'toolingcalibration_record': self.t_obj.all(),
                'form': form
            }
        )
        
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
            action_statement = 'Create ToolingCalibrationRecord with: ' + str(request.POST.dict())
            make_log(request, action_statement)
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.POST.get('c-end-date'):
            tool_item = ToolingCalibrationRecord.objects.get(pk=pk)
            tool_item.ActualCalibratedEndTime = request.POST.get('c-end-date')
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
            action_statement = (
                'Update Cali End Date with: ' + str(request.POST.get('c-end-date')) +
                ' for ' + tool_item.EquipmentNo
            )
            make_log(request, action_statement)
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.POST.get('m-start-date'):
            tool_item = ToolingCalibrationRecord.objects.get(pk=pk)
            tool_item.MQStartTime = request.POST.get('m-start-date')
            if not tool_item.CalibratedStartTime:
                tool_item.CalibratedStartTime = request.POST.get('m-start-date')
            if not tool_item.ActualCalibratedEndTime:
                tool_item.ActualCalibratedEndTime = request.POST.get('m-start-date')
            eq = EquipmentList.objects.get(EquipmentNo=tool_item.EquipmentNo)
            eq.Status = 'MQ'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            tool_item.save()
            action_statement = (
                'Update MQ Start Date with: ' + str(request.POST.get('m-start-date')) +
                ' for ' + tool_item.EquipmentNo
            )
            make_log(request, action_statement)
            return redirect('/emsapp/toolingcalibrationrecord')
        elif request.POST.get('m-end-date'):
            tool_item = ToolingCalibrationRecord.objects.get(pk=pk)
            tool_item.MQEndTime = request.POST.get('m-end-date')
            if not tool_item.CalibratedStartTime:
                tool_item.CalibratedStartTime = request.POST.get('m-end-date')
            if not tool_item.ActualCalibratedEndTime:
                tool_item.ActualCalibratedEndTime = request.POST.get('m-end-date')
            if not tool_item.MQStartTime:
                tool_item.MQStartTime = request.POST.get('m-end-date')
            eq = EquipmentList.objects.get(EquipmentNo=tool_item.EquipmentNo)
            eq.Status = 'Active'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.save()
            tool_item.save()
            action_statement = (
                'Update MQ End Date with: ' + str(request.POST.get('m-end-date')) +
                ' for ' + tool_item.EquipmentNo
            )
            make_log(request, action_statement)
            return redirect('/emsapp/toolingcalibrationrecord')
        else:
            return render(request, self.template_name, data)

class ToolingCalibrationRecordDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = ToolingCalibrationRecord
    template_name = 'emsapp/toolingcalibrationrecord/toolingcalibrationrecordDetail.html'
    permission_required = 'emsapp.view_toolingcalibrationrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/toolingcalibrationrecord/'

    def get_context_data(self, **kwargs):
        photo_list = []
        context = super(ToolingCalibrationRecordDetailView, self).get_context_data(**kwargs)
        pk = int(str(context['object']))
        photo_split = self.model.objects.filter(TicketNo=pk).values()[0]['PhotoLink'].split(';')
        context['PhotoLink'] = photo_split
        return context

''' Non Stock Transaction Record '''

class NonStockTransactionRecordView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_nonstocktransactionrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/nonstocktransactionrecord/'
    template_name = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html'
    context_object_name = 'nonstocktransaction_record'

    def get_queryset(self):
        return NonStockTransactionRecord.objects.filter(~Q(Deleted=True)).all()

    def search(self):
        qs = search(self)
        if qs:
            return render(self, 'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html', {'qs': qs})
        elif self.GET.dict():
            return render(
                self,
                'emsapp/nonstocktransactionrecord/nonstocktransactionrecord.html', {
                    'nonstocktransaction_record': ''
                }
            )
        else:
            return render(
                self,
                'emsapp/nonstocktransactionrecord/nonstocktransactionrecordSearch.html', {
                    'nonstocktransaction_record': NonStockTransactionRecord.objects.filter(~Q(Deleted=True))
                }
            )

class NonStockTransactionRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = n_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    ns_obj = NonStockTransactionRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, eqpk):
        form = create_form(request, eqpk)
        return render(
            request,
            self.template_name, {
                'equipment_list': self.e_obj.all(),
                'nonstocktransaction_record': self.ns_obj.all(),
                'form': form
            }
        )
        
    def post(self, request, eqpk):
        form = NonStockTransactionRecordForm(request.POST, request.FILES)
        data = {'equipment_list': self.e_obj.all(), 'nonstocktransaction_record': self.ns_obj.all(), 'form': form}
        if form.is_valid():
            form.save()
            eqno = form.cleaned_data['EquipmentNo']
            eq = EquipmentList.objects.get(EquipmentNo=eqno)
            eq.Status = 'InActive'
            eq.LastModifyUser = str(request.user)
            eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
            eq.LastNonStockShipDate = request.POST.get('TransactionReqTime')
            eq.Location = request.POST.get('TransactionTo')
            eq.save()
            action_statement = 'Create NonStockTransactionRecord with: ' + str(request.POST.dict())
            make_log(request, action_statement)
            return redirect('/emsapp/nonstocktransactionrecord')
        else:
            return render(request, self.template_name, data)

class NonStockTransactionRecordDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = NonStockTransactionRecord
    template_name = 'emsapp/nonstocktransactionrecord/nonstocktransactionrecordDetail.html'
    permission_required = 'emsapp.view_nonstocktransactionrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/nonstocktransactionrecord/'

    def get_context_data(self, **kwargs):
        photo_list = []
        context = super(NonStockTransactionRecordDetailView, self).get_context_data(**kwargs)
        pk = int(str(context['object']))
        photo_split = self.model.objects.filter(TicketNo=pk).values()[0]['PhotoLink'].split(';')
        context['PhotoLink'] = photo_split
        return context

''' General Transaction Record '''

class TransactionRecordView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'emsapp.view_transactionrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/transactionrecord/'
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
            return render(
                self,
                'emsapp/transactionrecord/transactionrecordSearch.html', {
                    'transaction_record': TransactionRecord.objects.filter(~Q(Deleted=True))
                }
            )

class TransactionRecordFormView(LoginRequiredMixin, PermissionRequiredMixin, generic.edit.FormView):
    template_name = 'emsapp/transactionrecord/transactionrecordForm.html'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = 'emsapp/equipmentlist/'
    permission_required = tr_admin_tuple
    e_obj = EquipmentList.objects.filter(~Q(Deleted=True))
    tr_obj = TransactionRecord.objects.filter(~Q(Deleted=True))
    
    def get(self, request, eqpk):
        form = create_form(request, eqpk)
        return render(
            request,
            self.template_name, {
                'equipment_list': self.e_obj.all(),
                'transaction_record': self.tr_obj.all(),
                'form': form
            }
        )
        
    def post(self, request, eqpk):
        form = TransactionRecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            description = form.cleaned_data['Description']
            trno = form.cleaned_data['TransactionTicketNo']
            if 'E_' in description:
                pos = description.find('E_')
                eqno = description[pos: pos+8]
                eq = EquipmentList.objects.get(EquipmentNo=eqno)
                eq.LastModifyUser = str(request.user)
                eq.LastModifyDate = datetime.date.today().strftime('%Y-%m-%d')
                eq.LastTransactionDate = request.POST.get('TransactionReqTime')
                eq.Location = request.POST.get('TransactionTo')
                eq.TransactionTicketNo = trno
                eq.save()
                action_statement = 'Create TransactionRecord with: ' + str(request.POST.dict())
                make_log(request, action_statement)
            return redirect('/emsapp/transactionrecord')
        else:
            return render(request, self.template_name, {'form': form})

class TransactionRecordDetailView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = TransactionRecord
    template_name = 'emsapp/transactionrecord/transactionrecordDetail.html'
    permission_required = 'emsapp.view_transactionrecord'
    login_url = '/emsapp/accounts/login/'
    redirect_field_name = '/emsapp/transactionrecord/'

    def get_context_data(self, **kwargs):
        photo_list = []
        context = super(TransactionRecordDetailView, self).get_context_data(**kwargs)
        pk = int(str(context['object']))
        photo_split = self.model.objects.filter(TicketNo=pk).values()[0]['PhotoLink'].split(';')
        context['PhotoLink'] = photo_split
        return context