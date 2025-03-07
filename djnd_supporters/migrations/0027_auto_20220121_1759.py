# Generated by Django 3.2.8 on 2022-01-21 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0026_donationcampaign_slack_report_channel"),
    ]

    operations = [
        migrations.AddField(
            model_name="donationcampaign",
            name="charged_unsuccessfully_email",
            field=models.IntegerField(
                blank=True,
                help_text="ID of email template on mautic for BT subscription charged unsuccessfully",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="donationcampaign",
            name="subscription_canceled_email",
            field=models.IntegerField(
                blank=True,
                help_text="ID of email template on mautic for BT cancel subscription",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="donationcampaign",
            name="subscription_charged_successfully",
            field=models.IntegerField(
                blank=True,
                help_text="ID of email template on mautic for BT subscription charged successfully",
                null=True,
            ),
        ),
    ]
