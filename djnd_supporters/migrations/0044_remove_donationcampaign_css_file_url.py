# Generated by Django 3.2.8 on 2024-09-18 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0043_auto_20240918_0840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donationcampaign',
            name='css_file_url',
        ),
    ]