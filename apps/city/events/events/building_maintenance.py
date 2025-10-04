from django.contrib import messages
from django.db.models import Sum

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.INFO
    TITLE = "Maintenance"

    maintenance: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.maintenance = self._calculate_maintenance()

    def get_probability(self):
        return (
            super().get_probability() if self.savegame.tiles.filter(building__maintenance_costs__gt=0).exists() else 0
        )

    def _calculate_maintenance(self):
        result = self.savegame.tiles.aggregate(sum_maintenance=Sum("building__maintenance_costs"))["sum_maintenance"]
        # Return None if there are no buildings with maintenance costs
        if result is None or (
            result == 0 and not self.savegame.tiles.filter(building__maintenance_costs__gt=0).exists()
        ):
            return None
        return result

    def get_effects(self):
        return (DecreaseCoins(coins=self.maintenance),)

    def get_verbose_text(self):
        return f"The treasury was set back by {self.maintenance} coin to maintain the citys buildings."
