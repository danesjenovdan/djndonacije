# Generated by Django 3.2.8 on 2023-01-17 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0032_alter_subscriber_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='donationcampaign',
            name='subtitle',
            field=models.CharField(default='', help_text='Subtitle shown in embed', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donationcampaign',
            name='title',
            field=models.CharField(default='', help_text='Title shown in embed', max_length=32),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='PredefinedAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('one_time_amount', models.BooleanField(default=True, help_text='Enable amount for one time donation')),
                ('recurring_amount', models.BooleanField(default=True, help_text='Enable amount for recurring donation')),
                ('donation_campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amounts', to='djnd_supporters.donationcampaign')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]