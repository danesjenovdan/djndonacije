# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-12-17 11:05
from __future__ import unicode_literals

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0017_remove_boundleitem_quantity"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="custom_mail",
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
