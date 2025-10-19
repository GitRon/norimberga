import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 10
    LEVEL = messages.SUCCESS
    TITLE = "Wandering Jugglers"

    initial_unrest: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_unrest = self.savegame.unrest
        self.lost_unrest = random.randint(1, 10)

    def get_probability(self) -> int | float:
        return super().get_probability() if self.savegame.unrest > 0 and self.savegame.population > 0 else 0

    def _prepare_effect_decrease_unrest(self) -> DecreaseUnrestAbsolute:
        return DecreaseUnrestAbsolute(lost_unrest=self.lost_unrest)

    def get_verbose_text(self) -> str:
        self.savegame.refresh_from_db()
        return (
            f"A group of wandering jugglers performs in town, entertaining the citizens. "
            f"The unrest drops by {self.initial_unrest - self.savegame.unrest}%."
        )
