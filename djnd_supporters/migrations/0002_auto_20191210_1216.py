# Generated by Django 2.2.1 on 2019-12-10 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='subscription_id',
        ),
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=1, default=0.0, max_digits=20)),
                ('gifts', models.ManyToManyField(related_name='gifts', to='djnd_supporters.Donation')),
                ('subscriber', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gifts', to='djnd_supporters.Subscriber')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
