from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from djnd_supporters.mautic_api import MauticApi
from djnd_supporters.models import Subscriber

mautic_api = MauticApi()


class Command(BaseCommand):
    help = "Fix semgment of users without segment in mautic"

    def handle(self, *args, **options):
        # segment_id = int(settings.MAUTIC_SEGMENT_ID_USERS_WITHOUT_SEGMENT)
        segment_id = int(41)
        data, status = mautic_api.getSegment(segment_id=segment_id)
        segments_data, status = mautic_api.getSegments()
        segment_ids = [int(key) for key in segments_data["lists"].keys()]
        segment_ids.remove(segment_id)

        update_needed = False

        for i in segment_ids:
            if i not in data["list"]["filters"][0]["filter"]:
                data["list"]["filters"][0]["filter"].append(i)
                data["list"]["filters"][0]["properties"]["filter"].append(i)
                update_needed = True

        if update_needed:
            new_data = {"filters": data["list"]["filters"]}

            response, status = mautic_api.patchSegment(
                segment_id=segment_id, data=new_data
            )
            if status == 200:
                print("Segment updated successfully")
            else:
                print("Failed to update segment")
