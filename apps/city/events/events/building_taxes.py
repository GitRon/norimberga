from django.contrib import messages
from django.db.models import Sum

from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.INFO

    savegame: Savegame
    taxes: int

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.taxes = self._calculate_taxes()

    def get_probability(self):
        return super().get_probability() if self.savegame.tiles.filter(building__taxes__gt=0).exists() else 0

    def _calculate_taxes(self):
        return self.savegame.tiles.aggregate(sum_taxes=Sum("building__taxes"))["sum_taxes"]

    def get_effects(self):
        return (IncreaseCoins(coins=self.taxes),)

    def get_verbose_text(self):
        return (
            f"Your loyal subjects were delighted to pay their fair amount of {self.taxes} coins as taxes to your city."
        )
