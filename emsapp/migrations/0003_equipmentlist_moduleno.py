# Generated by Django 2.1.10 on 2020-07-28 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emsapp', '0002_auto_20200728_0927'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipmentlist',
            name='ModuleNo',
            field=models.CharField(default='', max_length=255),
        ),
    ]
