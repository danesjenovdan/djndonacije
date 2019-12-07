# Generated by Django 2.2.1 on 2019-12-07 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djnd_supporters', '0002_auto_20190529_1152'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(blank=True, null=True)),
                ('token', models.TextField(default='1234567890')),
                ('image', models.ImageField(upload_to='images')),
                ('thumbnail', models.ImageField(upload_to='thumbs')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
