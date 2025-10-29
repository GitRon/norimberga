from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.services.prestige import PrestigeCalculationService
from apps.thread.conditions.abstract import AbstractThreadCondition


class PrestigeDefenseThread(AbstractThreadCondition):
    """
    Thread that activates when a city's prestige exceeds its defense value.
    A wealthy, prestigious city with weak defenses becomes a target for threats.
    """

    VERBOSE_NAME = "Prestige Exceeds Defense"

    def is_active(self) -> bool:
        """Check if prestige exceeds defense value."""
        prestige = self._get_prestige()
        defense = self._get_defense()
        return prestige > defense

    def get_intensity(self) -> int:
        """Calculate intensity as the difference between prestige and defense."""
        prestige = self._get_prestige()
        defense = self._get_defense()
        return max(0, prestige - defense)

    def _get_prestige(self) -> int:
        """Get current prestige value."""
        service = PrestigeCalculationService(savegame=self.savegame)
        return service.process()

    def _get_defense(self) -> int:
        """Get current defense value."""
        service = DefenseCalculationService(savegame=self.savegame)
        return service.process()
