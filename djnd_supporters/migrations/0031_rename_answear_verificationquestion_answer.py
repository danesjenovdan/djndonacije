# Generated by Django 3.2.8 on 2022-06-09 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0030_verificationquestion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='verificationquestion',
            old_name='answear',
            new_name='answer',
        ),
    ]