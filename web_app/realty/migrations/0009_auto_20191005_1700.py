# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-05 17:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0008_auto_20190929_2010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='parcel',
            field=models.IntegerField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='parcel',
            field=models.IntegerField(max_length=50, null=True),
        ),
    ]
