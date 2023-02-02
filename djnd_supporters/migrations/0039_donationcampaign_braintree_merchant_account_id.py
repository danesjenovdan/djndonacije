# Generated by Django 3.2.8 on 2023-02-02 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0038_alter_donationcampaign_subtitle'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcampaign',
            name='braintree_merchant_account_id',
            field=models.CharField(blank=True, help_text='ID of braintree merchant account.', max_length=128, null=True),
        ),
    ]
