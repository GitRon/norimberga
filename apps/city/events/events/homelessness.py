import random

from django.contrib import messages

from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.city.models import Savegame
from apps.city.services.building.housing import BuildingHousingService
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 90
    LEVEL = messages.WARNING
    TITLE = "Homelessness"

    savegame: Savegame
    initial_unrest: int

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.initial_unrest = self.savegame.unrest
        self.additional_unrest = random.randint(5, 8)

    def get_probability(self):
        return (
            super().get_probability()
            if self.savegame.population > BuildingHousingService().calculate_max_space() and self.savegame.unrest < 100
            else 0
        )

    def _prepare_effect_decrease_population(self):
        return IncreaseUnrestAbsolute(additional_unrest=self.additional_unrest)

    def get_verbose_text(self):
        self.savegame.refresh_from_db()
        return (
            f"Beggars and homeless folk are crowding the streets. The situation grows tenser by the day. The citys "
            f"unrest increased by {self.savegame.unrest - self.initial_unrest}%."
        )
