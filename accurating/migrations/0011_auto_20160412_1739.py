# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-12 17:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accurating', '0010_auto_20160412_1739'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trainingset',
            old_name='successful',
            new_name='success',
        ),
    ]
