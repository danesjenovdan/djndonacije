# Generated by Django 2.2.10 on 2021-01-20 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0014_donationcampaign_has_braintree_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcampaign',
            name='bt_subscription_email_template',
            field=models.IntegerField(blank=True, help_text='Id of email tempalte on mautic for braintree subscription donation', null=True),
        ),
        migrations.AlterField(
            model_name='donationcampaign',
            name='has_braintree_subscription',
            field=models.BooleanField(default=True, help_text='Enable braintree subscription donation'),
        ),
    ]