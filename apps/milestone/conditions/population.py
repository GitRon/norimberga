from apps.milestone.conditions.abstract import AbstractCondition


class MinPopulationCondition(AbstractCondition):
    def is_valid(self) -> bool:
        return self.savegame.population >= self.value
