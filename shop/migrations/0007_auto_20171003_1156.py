# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-03 11:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_auto_20171003_0907"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="info",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="phone",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
