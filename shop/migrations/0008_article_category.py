# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-03 12:41
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0007_auto_20171003_1156"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="Category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shop.Category",
            ),
        ),
    ]
