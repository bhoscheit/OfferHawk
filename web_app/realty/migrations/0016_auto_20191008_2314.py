# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-08 23:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0015_property_centralair'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='price_to_rent',
            field=models.FloatField(default=None, max_length=250),
        ),
    ]
