import importlib

from apps.savegame.models import Savegame
from apps.thread.conditions.abstract import AbstractThreadCondition
from apps.thread.models import ActiveThread, ThreadType


class ThreadCheckerService:
    """
    Service to check and update active threads for a savegame.

    Scans all ThreadType definitions, evaluates their conditions,
    and creates/updates/removes ActiveThread records accordingly.
    """

    def __init__(self, *, savegame: Savegame) -> None:
        self.savegame = savegame

    def process(self) -> list[ActiveThread]:
        """
        Check all thread types and update active threads.

        Returns:
            List of currently active threads after update
        """
        thread_types = ThreadType.objects.all()

        for thread_type in thread_types:
            self._check_thread_type(thread_type=thread_type)

        return list(self.savegame.active_threads.all())

    def _check_thread_type(self, *, thread_type: ThreadType) -> None:
        """
        Check a single thread type and update its active status.
        """
        # Instantiate the condition class
        condition = self._instantiate_condition(thread_type=thread_type)

        if condition is None:
            return

        # Check if thread should be active
        if condition.is_active():
            intensity = condition.get_intensity()
            self._activate_thread(thread_type=thread_type, intensity=intensity)
        else:
            self._deactivate_thread(thread_type=thread_type)

    def _instantiate_condition(self, *, thread_type: ThreadType) -> AbstractThreadCondition | None:
        """
        Dynamically import and instantiate the condition class.

        Returns:
            Condition instance or None if import fails
        """
        try:
            module_path, class_name = thread_type.condition_class.rsplit(".", 1)
            module = importlib.import_module(module_path)
            condition_class = getattr(module, class_name)
            return condition_class(savegame=self.savegame)
        except (ImportError, AttributeError, ValueError):
            return None

    def _activate_thread(self, *, thread_type: ThreadType, intensity: int) -> None:
        """
        Activate a thread or update its intensity if already active.
        """
        active_thread, created = ActiveThread.objects.get_or_create(
            savegame=self.savegame,
            thread_type=thread_type,
            defaults={
                "activated_at": self.savegame.current_year,
                "intensity": intensity,
            },
        )

        if not created:
            # Update intensity if thread already exists
            active_thread.intensity = intensity
            active_thread.save()

    def _deactivate_thread(self, *, thread_type: ThreadType) -> None:
        """
        Deactivate a thread if it's currently active.
        """
        ActiveThread.objects.filter(savegame=self.savegame, thread_type=thread_type).delete()
