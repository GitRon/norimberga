import random

from django.contrib import messages

from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 20
    LEVEL = messages.SUCCESS
    TITLE = "Wanted criminal"

    bounty: int

    def __init__(self):
        self.bounty = random.randint(100, 300)

    def _prepare_effect_increase_coins(self):
        return IncreaseCoins(coins=self.bounty)

    def get_verbose_text(self):
        return (
            f"The magistrate caught a wanted criminal. The malefactor was handed over to the Kings guard, rewarding "
            f"you with {self.bounty} coin."
        )
