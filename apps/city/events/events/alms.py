import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 15
    LEVEL = messages.SUCCESS
    TITLE = "Alms"

    savegame: Savegame
    initial_unrest: int

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.initial_unrest = self.savegame.unrest
        self.lost_unrest = random.randint(3, 5)

    def get_probability(self):
        return super().get_probability() if self.savegame.unrest > 0 and self.savegame.population > 0 else 0

    def _prepare_effect_decrease_population(self):
        return DecreaseUnrestAbsolute(lost_unrest=self.lost_unrest)

    def get_verbose_text(self):
        self.savegame.refresh_from_db()
        return (
            f"Members of the city council decided to provide alms for the sick and poor. The unrest drops by "
            f"{self.initial_unrest - self.savegame.unrest}%."
        )
