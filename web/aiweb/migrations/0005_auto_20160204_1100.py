# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-04 11:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aiweb', '0004_auto_20160131_0644'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_names', models.CharField(max_length=650)),
                ('scores', models.CharField(max_length=100)),
                ('statuses', models.CharField(max_length=100)),
                ('ranks', models.CharField(max_length=100)),
                ('game_message', models.CharField(max_length=100)),
                ('replay', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='submissions',
            field=models.ManyToManyField(to='aiweb.Submission'),
        ),
    ]