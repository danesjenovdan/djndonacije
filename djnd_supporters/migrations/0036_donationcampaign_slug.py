# Generated by Django 3.2.8 on 2023-01-17 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0035_auto_20230117_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcampaign',
            name='slug',
            field=models.CharField(default='', help_text='Lovercase name without spaces', max_length=32),
            preserve_default=False,
        ),
    ]