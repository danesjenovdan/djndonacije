# Generated by Django 3.2.8 on 2022-02-01 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0028_auto_20220125_0816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donationcampaign',
            name='web_hook_url',
            field=models.TextField(blank=True, help_text='Web hook for subscription events', null=True),
        ),
    ]
