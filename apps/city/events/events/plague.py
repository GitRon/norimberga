import random

from apps.city.events.effects.savegame.decrease_population_relative import DecreasePopulationRelative
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 5

    lost_population_percentage: float

    def __init__(self):
        self.lost_population_percentage = random.randint(10, 25) / 10

    def get_effects(self):
        return (DecreasePopulationRelative(lost_population_percentage=self.lost_population_percentage),)

    def get_verbose_text(self):
        localized_percentage = round(self.lost_population_percentage * 10)
        return (
            f"A horrific plague hit the city in its most vulnerable time. {localized_percentage}% of the population "
            f"died a tragic and slow death."
        )
