# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-05 13:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0013_auto_20180405_1309"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="is_sent",
            field=models.BooleanField(default=False),
        ),
    ]
