# Generated by Django 3.2.8 on 2022-01-25 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0027_auto_20220121_1759"),
    ]

    operations = [
        migrations.AddField(
            model_name="donationcampaign",
            name="edit_subscriptions_email_tempalte",
            field=models.IntegerField(
                blank=True,
                help_text="ID of email tempalte on mautic for edit subscrptions",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="donationcampaign",
            name="segment",
            field=models.IntegerField(
                blank=True,
                help_text="ID of default segment of this campaign",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="donationcampaign",
            name="welcome_email_tempalte",
            field=models.IntegerField(
                blank=True,
                help_text="ID of email tempalte on mautic to send on user registration",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="donationcampaign",
            name="bt_email_template",
            field=models.IntegerField(
                blank=True,
                help_text="ID of email tempalte on mautic for braintree donation",
                null=True,
            ),
        ),
    ]
