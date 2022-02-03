# Generated by Django 3.2.8 on 2022-01-14 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0025_donationcampaign_braintee_subscription_plan_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcampaign',
            name='slack_report_channel',
            field=models.TextField(default='#djnd-bot', help_text='Slack channel for events reporting. Starts with #'),
        ),
    ]