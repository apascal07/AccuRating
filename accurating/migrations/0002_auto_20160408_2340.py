# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-08 23:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accurating', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='reviewer_name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='review',
            name='reviewer_rank',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='trainingset',
            name='_criteria_weights',
            field=models.TextField(null=True),
        ),
    ]