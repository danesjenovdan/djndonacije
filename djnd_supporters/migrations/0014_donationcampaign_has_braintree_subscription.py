# Generated by Django 2.2.10 on 2021-01-20 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0013_auto_20210104_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcampaign',
            name='has_braintree_subscription',
            field=models.BooleanField(default=True, help_text='Enable braintree donation'),
        ),
    ]
