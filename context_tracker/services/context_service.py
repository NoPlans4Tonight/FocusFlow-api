from ..repositories.context_entry_repository import ContextEntryRepository
from datetime import datetime

class ServiceFactory:
    @staticmethod
    def get_context_entry_repository():
        return ContextEntryRepository()

    @staticmethod
    def get_context_service():
        return ContextService(ServiceFactory.get_context_entry_repository())

class ContextService:
    def __init__(self, context_entry_repo):
        self.context_entry_repo = context_entry_repo

    def log_context(self, user_id, activity, note):
        # End any active contexts for the user
        self.context_entry_repo.end_active_contexts(user_id)
        # Create a new context entry
        entry = self.context_entry_repo.create_context_entry(user_id, activity, note)
        return {'message': 'Context logged', 'entry_id': str(entry.id)}

    def get_user_contexts(self, user_id):
        # Retrieve all context entries for the user
        entries = self.context_entry_repo.get_all_contexts(user_id)
        return [
            {
                'id': str(entry.id),
                'activity': entry.activity,
                'note': entry.note,
                'start_time': entry.start_time,
                'end_time': entry.end_time
            } for entry in entries
        ]

    def delete_context(self, user_id, log_id):
        # Delete a specific context entry
        entry = self.context_entry_repo.get_context_by_id_and_user(log_id, user_id)
        if entry:
            entry.delete()
            return {'message': 'Log entry deleted successfully'}
        return {'error': 'Log entry not found'}

    def update_context(self, user_id, log_id, data):
        # Update a specific context entry
        entry = self.context_entry_repo.get_context_by_id_and_user(log_id, user_id)
        if not entry:
            return {'error': 'Log entry not found'}

        entry.activity = data.get('activity', entry.activity)
        entry.note = data.get('note', entry.note)

        start_time = data.get('start_time') or data.get('startTime')
        end_time = data.get('end_time') or data.get('endTime')

        if start_time:
            try:
                if start_time.endswith('Z'):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                else:
                    start_time = datetime.fromisoformat(start_time)
                entry.start_time = start_time
            except ValueError:
                pass

        if end_time:
            try:
                if end_time.endswith('Z'):
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                else:
                    end_time = datetime.fromisoformat(end_time)
                entry.end_time = end_time
            except ValueError:
                pass

        entry.save()
        return {'message': 'Log entry updated successfully'}

context_service = ServiceFactory.get_context_service()

def log_user_context(user_id, activity, note):
    return context_service.log_context(user_id, activity, note)

def stop_user_context(user_id):
    return context_service.stop_user_context(user_id)

def get_user_status(user_id):
    return context_service.get_user_status(user_id)

def get_user_entries(user_id):
    return context_service.get_user_contexts(user_id)