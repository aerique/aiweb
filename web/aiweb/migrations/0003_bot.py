# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-31 03:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aiweb', '0002_submission_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32)),
                ('game_id', models.CharField(max_length=32)),
                ('submission_id', models.CharField(max_length=100)),
                ('compile_time', models.DateTimeField(auto_now_add=True)),
                ('games_played', models.DecimalField(decimal_places=0, max_digits=16)),
            ],
        ),
    ]
