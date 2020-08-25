# A basement to set urls, in other words, this is an URLconfig file
# Urls will call class/fuction in views.py to handle request/response
# and further be called to urls.py in /ems

from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required, permission_required
from django.conf.urls.static import static
from django.conf import settings

'''
Note:
1. regex:   Routes to find.
2. view:    Functions in view.py.
3. name:    Can be found in .html file variables.
'''

app_name = 'emsapp'
urlpatterns = [
    # url(r'^home/$', views.HomeView.as_view(), name='home'),

    url(r'^accounts/login/$', views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'^home/info/$', views.HomeView.info, name='homeInfo'),
    url(r'^home/asset/$', views.HomeView.asset, name='homeAsset'),
    url(r'^home/tool/$', views.HomeView.tool, name='homeTool'),
    url(r'^home/nonstock/$', views.HomeView.nonstock, name='homeNonStock'),

    url(r'^trashbin/asset/$', views.TrashBinView.asset, name='trashBinAsset'),
    url(r'^trashbin/tool/$', views.TrashBinView.tool, name='trashBinTool'),
    url(r'^trashbin/nonstock/$', views.TrashBinView.nonstock, name='trashBinNonStock'),
    url(r'^trashbin/equipment/$', views.TrashBinView.equipment, name='trashBinEquipment'),
    url(r'^trashbin/trans/$', views.TrashBinView.trans, name='trashBinTrans'),
    url(r'^trashbin/equipment/search/$', views.TrashBinView.search, name='trashBinEquipmentSearch'),
    url(r'^trashbin/asset/search/$', views.TrashBinView.search, name='trashBinAssetSearch'),
    url(r'^trashbin/tool/search/$', views.TrashBinView.search, name='trashBinToolSearch'),
    url(r'^trashbin/nonstock/search/$', views.TrashBinView.search, name='trashBinNonStockSearch'),
    url(r'^trashbin/trans/search/$', views.TrashBinView.search, name='trashBinTransSearch'),

    url(r'^equipmentlist/$', views.EquipmentFormView.as_view(), name='equipmentForm'),
    url(r'^equipmentlist/(?P<pk>[0-9]+)/delete/$', views.delete, name='equipmentDelete'),
    url(r'^equipmentlist/(?P<pk>[0-9]+)/recovery/$', views.recovery, name='equipmentRecovery'),
    url(r'^equipmentlist/(?P<pk>[0-9]+)/update/$', views.update, name="equipmentUpdate"),
    url(r'^equipmentlist/(?P<pk>[0-9]+)/detail/$', views.EquipmentListDetailView.as_view(), name='equipmentDetail'),
    url(r'^equipmentlist/search/$', views.EquipmentFormView.search, name='equipmentSearch'),
    url(r'^equipmentlist/export/$', views.xlsx_export, name='equipmentExport'),
    url(r'^equipmentlist/import/$', views.xlsx_import, name='equipmentImport'),
    url(r'^equipmentlist/tool/check/$', views.ToolCheckView.as_view(), name='equipmentToolCheck'),
    url(r'^equipmentlist/asset/check/$', views.AssetCheckView.as_view(), name='equipmentAssetCheck'),
    url(r'^equipmentlist/nonstock/check/$', views.NonStockCheckView.as_view(), name='equipmentNonStockCheck'),
    url(r'^equipmentlist/trans/check/(?P<count>[0-9]+)/$', views.TransCheckView.as_view(), name='equipmentTransCheck'),

    url(r'^assetloanrecord/(?P<pk>[0-9]+)/form/$', views.AssetLoanRecordFormView.as_view(), name='assetLoanForm'),
    url(r'^assetloanrecord/$', views.AssetLoanRecordView.as_view(), name='assetLoanList'),
    url(r'^assetloanrecord/(?P<pk>[0-9]+)/delete/$', views.delete, name='assetLoanDelete'),
    url(r'^assetloanrecord/(?P<pk>[0-9]+)/recovery/$', views.recovery, name='assetLoanRecovery'),
    url(r'^assetloanrecord/(?P<pk>[0-9]+)/update/$', views.update, name="assetLoanUpdate"),
    url(r'^assetloanrecord/(?P<pk>[0-9]+)/detail/$', views.AssetLoanRecordDetailView.as_view(), name="assetLoanDetail"),
    url(r'^assetloanrecord/search/$', views.AssetLoanRecordView.search, name='assetLoanSearch'),
    url(r'^assetloanrecord/export/$', views.xlsx_export, name='assetLoanExport'),
    url(r'^assetloanrecord/import/$', views.xlsx_import, name='assetLoanImport'),

    url(r'^toolingcalibrationrecord/(?P<pk>[0-9]+)/form/$', views.ToolingCalibrationRecordFormView.as_view(), name='toolingCalibrationForm'),
    url(r'^toolingcalibrationrecord/$', views.ToolingCalibrationRecordView.as_view(), name='toolingCalibrationList'),
    url(r'^toolingcalibrationrecord/(?P<pk>[0-9]+)/delete/$', views.delete, name='toolingCalibrationDelete'),
    url(r'^toolingcalibrationrecord/(?P<pk>[0-9]+)/recovery/$', views.recovery, name='toolingCalibrationRecovery'),
    url(r'^toolingcalibrationrecord/(?P<pk>[0-9]+)/update/$', views.update, name="toolingCalibrationUpdate"),
    url(r'^toolingcalibrationrecord/(?P<pk>[0-9]+)/detail/$', views.ToolingCalibrationRecordDetailView.as_view(), name="toolingCalibrationDetail"),
    url(r'^toolingcalibrationrecord/search/$', views.ToolingCalibrationRecordView.search, name='toolingCalibrationSearch'),
    url(r'^toolingcalibrationrecord/export/$', views.xlsx_export, name='toolingCalibrationExport'),
    url(r'^toolingcalibrationrecord/import/$', views.xlsx_import, name='toolingCalibrationImport'),
    
    url(r'^nonstocktransactionrecord/(?P<eqpk>[0-9]+)/form/$', views.NonStockTransactionRecordFormView.as_view(), name='nonStockForm'),
    url(r'^nonstocktransactionrecord/$', views.NonStockTransactionRecordView.as_view(), name='nonStockList'),
    url(r'^nonstocktransactionrecord/(?P<pk>[0-9]+)/delete/$', views.delete, name='nonStockDelete'),
    url(r'^nonstocktransactionrecord/(?P<pk>[0-9]+)/recovery/$', views.recovery, name='nonStockRecovery'),
    url(r'^nonstocktransactionrecord/(?P<pk>[0-9]+)/update/$', views.update, name="nonStockUpdate"),
    url(r'^nonstocktransactionrecord/(?P<pk>[0-9]+)/detail/$', views.NonStockTransactionRecordDetailView.as_view(), name="nonStockDetail"),
    url(r'^nonstocktransactionrecord/search/$', views.NonStockTransactionRecordView.search, name='nonStockSearch'),
    url(r'^nonstocktransactionrecord/export/$', views.xlsx_export, name='nonStockExport'),
    url(r'^nonstocktransactionrecord/import/$', views.xlsx_import, name='nonStockImport'),

    url(r'^transactionrecord/(?P<eqpk>[0-9]+)/form/$', views.TransactionRecordFormView.as_view(), name='transForm'),
    url(r'^transactionrecord/$', views.TransactionRecordView.as_view(), name='transList'),
    url(r'^transactionrecord/(?P<pk>[0-9]+)/delete/$', views.delete, name='transDelete'),
    url(r'^transactionrecord/(?P<pk>[0-9]+)/recovery/$', views.recovery, name='transRecovery'),
    url(r'^transactionrecord/(?P<pk>[0-9]+)/update/$', views.update, name="transUpdate"),
    url(r'^transactionrecord/(?P<pk>[0-9]+)/detail/$', views.TransactionRecordDetailView.as_view(), name="transDetail"),
    url(r'^transactionrecord/search/$', views.TransactionRecordView.search, name='transSearch'),
    url(r'^transactionrecord/export/$', views.xlsx_export, name='transExport'),
    url(r'^transactionrecord/import/$', views.xlsx_import, name='transImport'),
]