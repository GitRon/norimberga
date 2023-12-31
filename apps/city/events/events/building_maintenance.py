from django.contrib import messages
from django.db.models import Sum

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.INFO
    TITLE = "Maintenance"

    savegame: Savegame
    maintenance: int

    def __init__(self):
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.maintenance = self._calculate_maintenance()

    def get_probability(self):
        return (
            super().get_probability()
            if self.savegame.tiles.filter(building__maintenance_costs__gt=False).exists()
            else 0
        )

    def _calculate_maintenance(self):
        return self.savegame.tiles.aggregate(sum_maintenance=Sum("building__maintenance_costs"))["sum_maintenance"]

    def get_effects(self):
        return (DecreaseCoins(coins=self.maintenance),)

    def get_verbose_text(self):
        return f"The treasury was set back by {self.maintenance} coin to maintain the citys buildings."
