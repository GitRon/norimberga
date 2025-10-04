import random
from math import ceil

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.WARNING
    TITLE = "Riots"

    initial_population: int
    lost_population: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_population = self.savegame.population
        self.lost_population = ceil((random.randint(5, 10) / 100) * self.initial_population)

    def get_probability(self) -> int | float:
        return super().get_probability() * self.savegame.unrest / 100 if self.savegame.population > 0 else 0

    def _prepare_effect_decrease_population(self) -> DecreasePopulationAbsolute:
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def get_verbose_text(self) -> str:
        # TODO(RV): sometimes this value is negative... no idea why
        self.savegame.refresh_from_db()
        return (
            f"The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{self.initial_population - self.savegame.population} human lives."
        )
