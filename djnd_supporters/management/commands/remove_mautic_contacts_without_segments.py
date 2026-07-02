from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from djnd_supporters.mautic_api import MauticApi
from djnd_supporters.models import Subscriber

mautic_api = MauticApi()


class Command(BaseCommand):
    help = "Remove Mautic contacts without segments"

    def add_arguments(self, parser):
        # add dry run argument
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Dry run, do not delete contacts",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        # segment_id = int(settings.MAUTIC_SEGMENT_ID_USERS_WITHOUT_SEGMENT)
        segment_id = int(41)
        data, status = mautic_api.getContacts(segment_alias="brez-segmenta")

        for contact in list(data["contacts"].values()):
            contact_id = contact["id"]
            user_segments, status = mautic_api.getSegmentsOfContact(
                contact_id=contact_id
            )
            subscriber = Subscriber.objects.filter(mautic_id=contact_id).first()
            if subscriber and subscriber.subscriptions.filter(is_active=True).exists():
                print(f"Subscriber {contact_id} has active subscriptions, skipping.")
                continue
            if (
                len(user_segments["lists"]) == 1
                and int(list(user_segments["lists"].keys())[0]) == segment_id
            ):
                if not dry_run:
                    print(f"Deleting contact {contact_id}...")
                    mautic_api.deleteContact(contact_id)
                else:
                    print(f"Dry run: would delete contact {contact_id}...")
                print(f"https://mautic.djnd.si/s/contacts/view/{contact_id}")

            else:
                print(f"Subscriber {contact_id} has segments, skipping.")
