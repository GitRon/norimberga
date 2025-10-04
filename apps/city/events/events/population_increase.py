from math import ceil

from django.contrib import messages

from apps.city.events.effects.savegame.increase_population_absolute import IncreasePopulationAbsolute
from apps.city.models import Savegame
from apps.city.services.building.housing import BuildingHousingService
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.INFO
    TITLE = "Population increase"

    YEARLY_POP_INCREASE_FACTOR = 0.05

    new_population: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_population = self.savegame.population
        self.new_population = max(ceil(self.savegame.population * self.YEARLY_POP_INCREASE_FACTOR), 1)

    def get_probability(self) -> int | float:
        return (
            super().get_probability()
            if self.initial_population < BuildingHousingService(savegame=self.savegame).calculate_max_space()
            else 0
        )

    def get_effects(self) -> tuple[IncreasePopulationAbsolute]:
        return (IncreasePopulationAbsolute(new_population=self.new_population),)

    def get_verbose_text(self) -> str:
        return f"Your fertile city welcomes {self.new_population} new inhabitants."
