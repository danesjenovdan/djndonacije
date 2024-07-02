from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from djnd_supporters.models import Subscriber
from djnd_supporters.mautic_api import MauticApi

mautic_api = MauticApi()

class Command(BaseCommand):
    help = 'Download croatian database'

    def handle(self, *args, **options):
        data, status = mautic_api.getContacts(without_token=True)
        for mautic_id, user_data in data['contacts'].items():
            subscriber = Subscriber.objects.filter(mautic_id=mautic_id)
            if subscriber:
                print(f"Subscriber {mautic_id} already exists")
                continue
            if not user_data['fields']['all']['token']:
                new_subscriber = Subscriber(mautic_id=mautic_id)
                new_subscriber.save()
                new_subscriber.update_contact(
                    {"token": new_subscriber.token}
                )
