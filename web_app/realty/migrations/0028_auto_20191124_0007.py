# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-11-24 00:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realty', '0027_property_one_cf'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='absent_owner',
            field=models.CharField(max_length=75, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='absent_owner_city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='absent_owner_mail',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='absent_owner_state',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='absent_owner_zip',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='vacant_owner',
            field=models.CharField(max_length=75, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='vacant_owner_city',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='vacant_owner_mail',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='vacant_owner_state',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='vacant_owner_zip',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
