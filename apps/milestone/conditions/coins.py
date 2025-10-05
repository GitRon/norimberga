from apps.milestone.conditions.abstract import AbstractCondition


class MinCoinsCondition(AbstractCondition):
    """Check if savegame has at least the specified amount of coins."""

    VERBOSE_NAME = "Minimum Coins"

    def is_valid(self) -> bool:
        return self.savegame.coins >= self.value
