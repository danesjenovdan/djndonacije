# Generated by Django 2.2.3 on 2019-12-14 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0005_subscriber_nonce'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='nonce',
        ),
        migrations.AddField(
            model_name='donation',
            name='nonce',
            field=models.TextField(blank=True, null=True),
        ),
    ]