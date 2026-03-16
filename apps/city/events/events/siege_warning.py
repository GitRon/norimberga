from django.contrib import messages

from apps.city.services.siege.announcement import SiegeAnnouncementService
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import PendingSiege


class Event(BaseEvent):
    PROBABILITY = 8
    LEVEL = messages.WARNING
    TITLE = "Scout Report: Enemy Force Approaching"

    _pending_siege: PendingSiege

    def get_probability(self) -> int:
        already_pending = PendingSiege.objects.has_unresolved(savegame=self.savegame)
        return 0 if already_pending else super().get_probability()

    def get_effects(self) -> list:
        return []

    def process(self) -> str:
        self._pending_siege = SiegeAnnouncementService(savegame=self.savegame).process()
        return self.get_verbose_text()

    def get_verbose_text(self) -> str:
        direction = PendingSiege.Direction(self._pending_siege.direction).label
        years_away = self._pending_siege.attack_year - self.savegame.current_year

        return (
            f"Scouts report an enemy force of approximately ~{self._pending_siege.announced_strength} warriors "
            f"massing to the {direction}. "
            f"They are expected to arrive in {years_away} year{'s' if years_away != 1 else ''}."
        )
