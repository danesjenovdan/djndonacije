# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-26 11:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0011_auto_20171004_1503"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="mergable",
            field=models.BooleanField(default=False),
        ),
    ]
