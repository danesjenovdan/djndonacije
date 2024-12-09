# Generated by Django 3.2.8 on 2022-01-14 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0023_donationcampaign_web_hook_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subscriber",
            name="braintree_id",
        ),
        migrations.RemoveField(
            model_name="subscriber",
            name="uid",
        ),
        migrations.AddField(
            model_name="subscriber",
            name="customer_id",
            field=models.TextField(
                blank=True, help_text="Braintree customer id", null=True
            ),
        ),
    ]
