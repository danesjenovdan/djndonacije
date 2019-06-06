# Generated by Django 2.2.1 on 2019-05-29 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gift',
            options={'verbose_name': 'Gift', 'verbose_name_plural': 'Gifts'},
        ),
        migrations.AlterModelOptions(
            name='supporter',
            options={'verbose_name': 'Supporter', 'verbose_name_plural': 'Supporters'},
        ),
        migrations.AlterField(
            model_name='gift',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gifts', to='djnd_supporters.Supporter'),
        ),
    ]
