from apps.milestone.conditions.abstract import AbstractCondition


class MinPopulationCondition(AbstractCondition):
    """Check if savegame has reached minimum population."""

    VERBOSE_NAME = "Minimum Population"

    def is_valid(self) -> bool:
        return self.savegame.population >= self.value
