# Generated by Django 2.2.1 on 2020-01-17 11:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0018_article_custom_mail"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="variant_of",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variants",
                to="shop.Article",
                verbose_name="variant of",
            ),
        ),
    ]
