# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-06-14 02:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0033_auto_20200614_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='family',
            field=models.FloatField(default=None, null=True),
        ),
    ]
