import random

from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 25

    lost_population: int

    def __init__(self):
        self.lost_population = random.randint(5, 10)

    def get_effects(self):
        # TODO(RV): die zahlen stimmen nicht, da die grenzen erst vom effekt berechnet werden...
        return (DecreasePopulationAbsolute(lost_population=self.lost_population),)

    def get_verbose_text(self):
        return (
            f"The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{self.lost_population} human lives."
        )
