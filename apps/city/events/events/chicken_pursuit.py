from django.contrib import messages

from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 1
    LEVEL = messages.INFO
    TITLE = "Chicken Pursuit"

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)

    def get_probability(self) -> int | float:
        return super().get_probability() if self.savegame.population > 0 else 0

    def get_verbose_text(self) -> str:
        return (
            "A chicken escapes a coop and half the street joins the chase, "
            "shouting tactical advice as if it's a military campaign."
        )
