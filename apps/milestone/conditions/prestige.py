from apps.city.services.prestige import PrestigeCalculationService
from apps.milestone.conditions.abstract import AbstractCondition


class MinPrestigeCondition(AbstractCondition):
    """Check if savegame has reached minimum prestige."""

    VERBOSE_NAME = "Minimum Prestige"

    def is_valid(self) -> bool:
        service = PrestigeCalculationService(savegame=self.savegame)
        current_prestige = service.process()
        return current_prestige >= self.value
