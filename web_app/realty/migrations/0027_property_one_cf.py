# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-03 20:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0026_auto_20191103_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='one_cf',
            field=models.FloatField(null=True),
        ),
    ]
