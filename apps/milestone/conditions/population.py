from apps.city.models import Savegame
from apps.milestone.conditions.abstract import AbstractCondition


class MinPopulationCondition(AbstractCondition):
    min_population: int

    def __init__(self, *, min_population: int) -> None:
        self.min_population = min_population

    def is_valid(self, *, savegame: Savegame) -> bool:
        return savegame.population >= self.min_population
