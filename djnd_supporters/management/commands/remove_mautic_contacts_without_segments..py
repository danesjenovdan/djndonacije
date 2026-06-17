from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from djnd_supporters.mautic_api import MauticApi
from djnd_supporters.models import Subscriber

mautic_api = MauticApi()


class Command(BaseCommand):
    help = "Remove Mautic contacts without segments"

    def handle(self, *args, **options):
        # segment_id = int(settings.MAUTIC_SEGMENT_ID_USERS_WITHOUT_SEGMENT)
        segment_id = int(41)
        data, status = mautic_api.getContacts(segment_alias="brez-segmenta")

        for contact in data["contacts"].values():
            contact_id = contact["id"]
            user_segments, status = mautic_api.getSegmentsOfContact(
                contact_id=contact_id
            )
            if (
                len(user_segments["lists"]) == 1
                and int(list(user_segments["lists"].keys())[0]) == segment_id
            ):
                mautic_api.deleteContact(contact["id"])
