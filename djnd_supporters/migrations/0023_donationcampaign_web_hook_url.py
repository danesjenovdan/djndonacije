# Generated by Django 3.2.8 on 2022-01-13 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0022_rename_nonce_subscription_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="donationcampaign",
            name="web_hook_url",
            field=models.CharField(
                blank=True,
                help_text="Web hook for subscription events",
                max_length=32,
                null=True,
            ),
        ),
    ]
