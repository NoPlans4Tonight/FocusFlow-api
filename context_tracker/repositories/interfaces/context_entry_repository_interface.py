from abc import ABC, abstractmethod

class ContextEntryRepositoryInterface(ABC):
    @abstractmethod
    def create_context_entry(self, user_id, activity, note):
        pass

    @abstractmethod
    def end_active_contexts(self, user_id):
        pass

    @abstractmethod
    def get_active_context(self, user_id):
        pass

    @abstractmethod
    def get_all_contexts(self, user_id):
        pass

    @abstractmethod
    def get_context_by_id_and_user(self, log_id, user_id):
        pass
