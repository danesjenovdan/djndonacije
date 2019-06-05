# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-03 09:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20171002_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='image',
            field=models.ImageField(blank=True, max_length=1000, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='order',
            name='basket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='shop.Basket'),
        ),
    ]
