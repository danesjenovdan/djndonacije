# Generated by Django 2.2.1 on 2019-12-10 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0003_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='is_assigned',
            field=models.BooleanField(default=True),
        ),
    ]
