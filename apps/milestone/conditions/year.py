from apps.milestone.conditions.abstract import AbstractCondition


class MinYearCondition(AbstractCondition):
    """Check if savegame has reached at least the specified year."""

    VERBOSE_NAME = "Minimum Year"

    def is_valid(self) -> bool:
        return self.savegame.current_year >= self.value
