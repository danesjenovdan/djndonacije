# Generated by Django 2.2.1 on 2019-12-10 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0002_auto_20191210_1216"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
