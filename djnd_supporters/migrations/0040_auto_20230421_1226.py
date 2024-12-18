# Generated by Django 3.2.8 on 2023-04-21 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djnd_supporters", "0039_donationcampaign_braintree_merchant_account_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="donationcampaign",
            name="add_to_newsletter_confirmation_required",
            field=models.BooleanField(
                default=False,
                help_text="Add to newsletter confirmation required",
                verbose_name="Add to newsletter confirmation required",
            ),
        ),
        migrations.AlterField(
            model_name="donationcampaign",
            name="welcome_email_tempalte",
            field=models.IntegerField(
                blank=True,
                help_text="Welcome or confirmation email ID",
                null=True,
                verbose_name="Welcome or confirmation email ID",
            ),
        ),
    ]
