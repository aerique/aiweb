# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-13 06:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aiweb', '0007_auto_20160210_0325'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='mu',
            field=models.FloatField(default=50.0),
        ),
        migrations.AddField(
            model_name='submission',
            name='sigma',
            field=models.FloatField(default=10.0),
        ),
        migrations.AddField(
            model_name='submission',
            name='skill',
            field=models.FloatField(default=20.0),
        ),
    ]
