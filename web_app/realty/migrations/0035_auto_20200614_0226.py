# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-06-14 02:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0034_auto_20200614_0223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='rent',
            field=models.CharField(default=None, max_length=250, null=True),
        ),
    ]
