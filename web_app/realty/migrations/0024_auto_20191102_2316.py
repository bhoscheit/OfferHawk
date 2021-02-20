# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-02 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0023_property_taxes'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='pfc',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='pfc_date',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='pfc_owner',
            field=models.CharField(max_length=75, null=True),
        ),
    ]