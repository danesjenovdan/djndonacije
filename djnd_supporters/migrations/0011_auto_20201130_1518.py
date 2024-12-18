# Generated by Django 2.2.10 on 2020-11-30 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0010_recurringdonation"),
    ]

    operations = [
        migrations.AddField(
            model_name="donation",
            name="is_paid",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="donation",
            name="payment_method",
            field=models.CharField(default="braintree", max_length=50),
        ),
        migrations.AddField(
            model_name="donation",
            name="reference",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
