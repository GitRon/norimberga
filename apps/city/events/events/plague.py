import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_population_relative import DecreasePopulationRelative
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 5
    LEVEL = messages.ERROR
    TITLE = "Plague"

    lost_population_percentage: float

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.lost_population_percentage = random.randint(10, 25) / 100

    def get_probability(self) -> int | float:
        return super().get_probability() if self.savegame.population > 0 else 0

    def get_effects(self) -> tuple[DecreasePopulationRelative]:
        return (DecreasePopulationRelative(lost_population_percentage=self.lost_population_percentage),)

    def get_verbose_text(self) -> str:
        localized_percentage = round(self.lost_population_percentage * 10)
        return (
            f"A horrific plague hit the city in its most vulnerable time. {localized_percentage}% of the population "
            f"died a tragic and slow death."
        )
