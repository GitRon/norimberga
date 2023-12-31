import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_population_relative import DecreasePopulationRelative
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 5
    LEVEL = messages.ERROR
    TITLE = "Plague"

    savegame: Savegame
    lost_population_percentage: float

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.lost_population_percentage = random.randint(10, 25) / 100

    def get_probability(self):
        return super().get_probability() if self.savegame.population > 0 else 0

    def get_effects(self):
        return (DecreasePopulationRelative(lost_population_percentage=self.lost_population_percentage),)

    def get_verbose_text(self):
        localized_percentage = round(self.lost_population_percentage * 10)
        return (
            f"A horrific plague hit the city in its most vulnerable time. {localized_percentage}% of the population "
            f"died a tragic and slow death."
        )
