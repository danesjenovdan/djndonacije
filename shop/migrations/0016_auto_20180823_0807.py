# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-23 08:07
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0015_order_is_on_cebelca"),
    ]

    operations = [
        migrations.CreateModel(
            name="BoundleItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("modified", models.DateTimeField(blank=True, null=True)),
                ("quantity", models.IntegerField(default=1)),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="in_boundle",
                        to="shop.Article",
                    ),
                ),
                (
                    "boundle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="boundle_items",
                        to="shop.Article",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="article",
            name="articles",
            field=models.ManyToManyField(
                blank=True, through="shop.BoundleItem", to="shop.Article"
            ),
        ),
    ]
