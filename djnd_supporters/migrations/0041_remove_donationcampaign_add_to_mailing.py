# Generated by Django 3.2.8 on 2023-11-14 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0040_auto_20230421_1226"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="donationcampaign",
            name="add_to_mailing",
        ),
    ]
