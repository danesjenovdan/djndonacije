from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from djnd_supporters import models
from djnd_supporters.flik_utils import create_flik_request
from djnd_supporters.mautic_api import MauticApi

mautic_api = MauticApi()


class Command(BaseCommand):

    def handle(self, *args, **options):
        today = date.today()
        if today.day == 1:
            # check if there any active flik subscriptions which dont have a transactions for
            # the previous month, if there are, create a flik request for them
            previous_month = today.month - 1
            if not previous_month == 0:
                transactions = models.Transaction.objects.filter(
                    created__month=previous_month,
                    created__year=today.year,
                    payment_method="flik",
                    subscription__isnull=False,
                )
                subscriptions = models.Subscription.objects.filter(
                    type="flik",
                    is_active=True,
                ).exclude(
                    id__in=transactions.values_list("subscription_id", flat=True),
                )
                for subscription in subscriptions:
                    try:
                        create_flik_request(subscription)
                    except Exception as e:
                        print(
                            f"Failed to create flik request for subscription {subscription.id}: {str(e)}"
                        )
        # get all transactions for the current month, that are paid with flik and have a subscription
        transactions = models.Transaction.objects.filter(
            created__month=today.month,
            created__year=today.year,
            payment_method="flik",
            subscription__isnull=False,
        )
        # get all active subscriptions for campaigns that have flik subscription,
        # that don't have a transaction for the current month
        subscriptions = models.Subscription.objects.filter(
            type="flik",
            is_active=True,
        ).exclude(
            id__in=transactions.values_list("subscription_id", flat=True),
        )

        for subscription in subscriptions:
            # skip subscriptions created after the day of the month of today
            if subscription.created.day > today.day:
                continue
            try:
                create_flik_request(subscription)
            except Exception as e:
                print(
                    f"Failed to create flik request for subscription {subscription.id}: {str(e)}"
                )
