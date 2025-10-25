import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 15
    LEVEL = messages.SUCCESS
    TITLE = "Alms"

    initial_unrest: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_unrest = self.savegame.unrest
        self.lost_unrest = random.randint(3, 5)

    def get_probability(self) -> int | float:
        return super().get_probability() if self.savegame.unrest > 0 and self.savegame.population > 0 else 0

    def _prepare_effect_decrease_population(self) -> DecreaseUnrestAbsolute:
        return DecreaseUnrestAbsolute(lost_unrest=self.lost_unrest)

    def get_verbose_text(self) -> str:
        self.savegame.refresh_from_db()
        return (
            f"Members of the city council decided to provide alms for the sick and poor. The unrest drops by "
            f"{self.initial_unrest - self.savegame.unrest}%."
        )
