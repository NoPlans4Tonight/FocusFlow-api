from ..models import ContextEntry
from django.utils.timezone import now

class ContextEntryRepository:
    def create_context_entry(self, user_id, activity, note):
        return ContextEntry.objects.create(
            user_id=user_id,
            activity=activity,
            note=note,
            start_time=now()
        )

    def end_active_contexts(self, user_id):
        return ContextEntry.objects.filter(user_id=user_id, end_time__isnull=True).update(end_time=now())

    def get_active_context(self, user_id):
        return ContextEntry.objects.filter(user_id=user_id, end_time__isnull=True).first()

    def get_all_contexts(self, user_id):
        return ContextEntry.objects.filter(user_id=user_id).order_by('-start_time')

    def get_context_by_id_and_user(self, log_id, user_id):
        return ContextEntry.objects.filter(id=log_id, user_id=user_id).first()