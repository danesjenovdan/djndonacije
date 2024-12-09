# Generated by Django 3.2.8 on 2023-01-30 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0036_donationcampaign_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="donationcampaign",
            name="name",
            field=models.CharField(
                help_text="Name of donation campaign", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="donationcampaign",
            name="subtitle",
            field=models.CharField(
                blank=True,
                help_text="Subtitle shown in embed",
                max_length=32,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="donationcampaign",
            name="title",
            field=models.CharField(help_text="Title shown in embed", max_length=256),
        ),
    ]
