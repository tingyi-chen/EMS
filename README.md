# MIKI Code Explanation
## Reference
1. [Tutorial](https://docs.djangoproject.com/en/2.1/intro/tutorial01/)
2. [Field](https://docs.djangoproject.com/en/2.1/ref/models/fields/#common-model-field-options)
3. [DB Query](https://docs.djangoproject.com/en/2.1/topics/db/queries)
4. [Model Form](https://docs.djangoproject.com/en/2.1/topics/forms/modelforms/)
## Python files
`views.py`
1. Define all pages that show to users.
2. Interact with .html files, i.e. transfer data, redirect url...
3. Control requests and responses, finally render to users.
4. Functions that call the database is written here.

`urls.py`
1. Define all urls, also, these urls can pass variables.

## Login
`@login_requrired`
1. Function decorator (function-based).
2. Only logged-in users can call the decorated funtion.

`LoginRequriredMixin`
1. Class mixin (class-based).
2. Only logged-in users can access the mixined class.

`login_url`
1. The assignment is coupled with LoginRequiredMixin.
2. Check if the user is logged in.

`redirect_field_name`
1. This variable simultaneously exists if login_url is assigned.
2. After logging in, django will automatically redirect to this url.

## Permission
`@permission_requrired`
1. Function decorator (function-based).
2. Only authenticated users can call the decorated funtion.

## Variables
`permission_required`
1. This assignment is coupled with PermissionRequiredMixin.
2. Determine which permission should the user have?
3. If the user does not have required permissions, django will automatically redirect to login page.


`template_name`
1. Override the default .html file path and name.

`context_object_name`
1. Override the default variable that sends to .html files.

`get_queryset`
1. Default function binding with generic.ListView, and then return "django QuerySet object".
2. What returns Will be passed to context_object_name.
3. Return Model.objects.all() passes data to context_object_name.

## Functions
`def make_log(request, action)`
1. Create log for what users have done.

`def create_validation(...)`
1. Check if AssetNo is filled in when "EquipmentType: Asset" is checked, so do other equipment type.

`def update(request, pk)`
1. Split the request url, map with `model_list` and then assign the returned `ModelObject` to `model`.
2. What assigns will be further checked with if statement and finish corresponding work.

`def delete(request, pk)`
1. Split the request url, map with `model_list` and then assign the returned `ModelObject` to `model`.
2. Find `TicketNo` equals to `pk` and change `Deleted=False` to `True`, rather than delete from the database.

`def recovery(request, pk)`
1. Change `Deleted=False` to `True`.

`def create_form(...)`
1. Check if the splitted url map with the database model.
2. Find the maxima pk or maxima CountIndex/TicketNo, and then +1
3. If the model does not equal to `EquipmentList`, some basic information is auto-filled.

`def search(request)`
1. `__icontains` will check if the searhing query match with data in the database, and ignore the uppercase or lowercase.

`def xlsx_export(request)`
1. Export to Desktop.

`def xlsx_import(request)`
1. Please be aware of the import format.
2. There are some existing error handling mechanisms, which is helpful when debugging.

## View
`class ToolCheckView(...)`
1. Show tools if they are going to be calibrated.
2. Automatically create `demo.docx`, i.e. calibration list.
3. Automatically change the date related to calibration, modifying `user` and `status`.

`class AssetCheckView(...)`
1. Show assets if they are going to be returned from vendors.
2. Automatically change the date related to loan, modifying `user` and `status`.

`class NonStockCheckView(...)`
1. Show objects if they have `NonStockNo`
2. Automatically change the date related to transaction, modifying `user` and `status`.

`class NonStockCheckView(...)`
1. Click to add what to transact.
2. Automatically change the date related to transaction, modifying `user` and `status`.

`class HomeView(...)`
1. `labels` and `data` will be passed to javascript region of `/overview/xxxx.html`
2. Where `xxxx` can be `asset`, `tool` and `nonstock`

`class ...FormView(...)`
1. `if...elif...else` inside `def search(self)` provides proper mechanism of search modal.
2. Codes inside `def get(self, request)` check if data has `AssetNo` but is not assigned to `EquipmentType: Asset`
3. `instance = form.save(commit=False)` inside `def post(self, request)` provides proper morphology modification to `PhotoLink` before submitting

`class ...DetailView(...)`
1. Codes inside `get_context_data(...)` show multiple photos.

## Customization
### Photo Path
1. Use `Ctrl+F` to find `root_url`.
2. Change `'/photo/'` in `root_url = photo_url.rsplit('/', 1)[0] + '/photo/'`
3. Find `photo_list.append('photo/'+ photo)` and change `'photo/'` to whatever.
4. `photo_list.append('photo/'+ photo)` may be found for 4 times.
### Imported File Path
Change `location="..."` and `base_url="..."`.
```=python
#views.py

def xlsx_import(request):
    ...
    
    fs = FileSystemStorage(location="media/import", base_url="/media/import/")
    
    ...
```
### Uploaded File Path
Change `upload_to`.
```=python
# models.py
class AssetLoanRecord(models.Model):
    ...
    
    AssetLoanDocument = models.FileField(blank=True, upload_to='AssetLoanDocument')
    
    ...
...

class ToolingCalibrationRecord(models.Model):
    ...
    
    CalibratedReport = models.FileField(blank=True, upload_to='CalibratedReport')
    
    ...
...
```
### Export Path
Change the parameter of `df.to_excel()`.
```=python
# views.py

def xlsx_export(request):
    ...
    
    df.to_excel('C:\\Users\\kchen171277\\Desktop\\' + export_name, index=False)
    
    ...
```
### Digits of Automatically Created Numbers
Change `'06d'`, which means 6 digits to `'07d'`, which means 7 digits.

### Tool Reminder
Change the value of `tool_date_delta`
```=python
# views.py

class HomeView(...):
    ...
    def tool(self):
        ...
        
        tool_list = EquipmentList.objects.filter(EquipmentType__icontains='Tool').filter(Status='Active').filter(~Q(Deleted=True)).order_by('NextCalibratedDate').values()
        for tool in tool_list:
            next_date = tool['NextCalibratedDate']
            if next_date:
                tool_date_delta = (next_date - datetime.date.today()).days
                if tool_date_delta <= 60:
                    data['Tool'].append({'No': tool['ToolingNo'], 'Date': tool_date_delta})
        
        ...
    ...
```
### Asset Reminder
Change the value of `asset_date_delta`.
```=python
# views.py

class HomeView(...):
    def asset(self):
        ...
        
        asset_list = EquipmentList.objects.filter(EquipmentType__icontains='Asset').filter(~Q(Deleted=True)).order_by('AssetLoanedReturnDate').values()
        for asset in asset_list:
            return_date = asset['AssetLoanedReturnDate']
            if return_date:
                asset_date_delta = (return_date - datetime.date.today()).days
                if asset_date_delta <= 60:
                    data['Asset'].append({'No': asset['AssetNo'], 'Date': asset_date_delta})
        
        ...
    ...
```
### NonStock Reminder
Change the value of `ns_date_delta`.
```=python
# views.py

class HomeView(...):
    ...
    def nonstock(self):
        ...
        
        ns_list = EquipmentList.objects.filter(EquipmentType__icontains='NonS').filter(Status='InActive').filter(~Q(Deleted=True)).order_by('LastNonStockShipDate').values()
        for ns in ns_list:
            date = ns['LastNonStockShipDate']
            if date:
                ns_date_delta = (datetime.date.today() - date).days
                if ns_date_delta >= 180:
                    data['NonStock'].append({'No': ns['NonStockNo'], 'Date': ns_date_delta})
                    
        ...
    ...
```
### NextCalibratedDate
1. Use `Ctrl+F` to find `NextCalibratedDate` in `views.py`.
2. Change `relativedelta(years=+1)` to `relativedelta(days=1)` or `relativedelta(months=1)`.
3. Be aware of `month"s"`, `day"s"` and `year"s"`. `s` is needed
### PlanCalDate
1. Use `Ctrl+F` to find `PlanCalDate` in `views.py`.
2. Change `relativedelta(months=1)` to `relativedelta(days=1)` or `relativedelta(years=1)`.
3. Be aware of `month"s"`, `day"s"` and `year"s"`. `s` is needed