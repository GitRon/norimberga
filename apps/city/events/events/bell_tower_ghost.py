from django.contrib import messages

from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 15
    LEVEL = messages.INFO
    TITLE = "Bell Tower Ghost"

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)

    def get_probability(self) -> int | float:
        return super().get_probability() if self.savegame.population > 0 else 0

    def get_verbose_text(self) -> str:
        return (
            "Someone swears they saw a pale figure up in the tower. Turns out it's the new bell ringer avoiding taxes."
        )
