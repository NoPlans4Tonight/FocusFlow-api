from ..context_entry import ContextEntry
from django.utils.timezone import now

class ContextEntryFactory:
    @staticmethod
    def create(user_id, activity, note):
        return ContextEntry.objects.create(
            user_id=user_id,
            activity=activity,
            note=note,
            start_time=now()
        )
