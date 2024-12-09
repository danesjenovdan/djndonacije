from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from djnd_supporters.models import DonationCampaign


class Command(BaseCommand):
    help = "Download croatian database"

    def handle(self, *args, **options):
        self.stdout.write("\n")
        self.stdout.write("Setting development setup")
        donation_campaign = DonationCampaign(
            name="DJND",
            upn_name="DJND donacija",
            has_upn=True,
            has_braintree=True,
            has_braintree_subscription=True,
            upn_email_template=1,
            bt_email_template=1,
            bt_subscription_email_template=1,
            segment=1,
        )
        donation_campaign.save()
