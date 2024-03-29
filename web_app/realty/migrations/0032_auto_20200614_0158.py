# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-06-14 01:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0031_auto_20200614_0153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='bedrooms',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)], default=3, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='car_spaces',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3)], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_type',
            field=models.IntegerField(choices=[(1, 'All'), (2, 'SFH'), (3, 'Condo'), (4, 'Duplex'), (5, 'Triplex'), (6, 'Quadruplex'), (7, '5+ Units')], default=1, null=True),
        ),
    ]
