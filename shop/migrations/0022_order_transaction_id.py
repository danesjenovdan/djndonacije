# Generated by Django 3.2.8 on 2022-01-21 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0021_auto_20201130_1518"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="transaction_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
