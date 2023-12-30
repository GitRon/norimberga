from math import ceil

from apps.city.events.effects.savegame.increase_population_absolute import IncreasePopulationAbsolute
from apps.city.models import Savegame
from apps.city.services.building.housing import BuildingHousingService
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100

    YEARLY_POP_INCREASE_FACTOR = 0.05

    savegame: Savegame
    new_population: int

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.initial_population = self.savegame.population
        self.new_population = max(ceil(self.savegame.population * self.YEARLY_POP_INCREASE_FACTOR), 1)

    def get_probability(self):
        return (
            super().get_probability() if self.initial_population < BuildingHousingService().calculate_max_space() else 0
        )

    def get_effects(self):
        return (IncreasePopulationAbsolute(new_population=self.new_population),)

    def get_verbose_text(self):
        return f"Your fertile city welcomes {self.new_population} new inhabitants."
