# Generated by Django 3.2.8 on 2023-01-12 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0031_rename_answear_verificationquestion_answer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscriber",
            name="token",
            field=models.TextField(default=""),
        ),
    ]
