# Generated by Django 2.2.3 on 2019-12-14 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0004_donation_is_assigned'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='nonce',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
