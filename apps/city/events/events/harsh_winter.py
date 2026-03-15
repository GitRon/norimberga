import random

from django.contrib import messages

from apps.city.events.effects.building.damage_wall import DamageWall
from apps.city.models import Tile
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 15
    LEVEL = messages.WARNING
    TITLE = "Harsh Winter"

    wall_tiles: list[Tile]
    damage: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.damage = random.randint(15, 20)
        self.wall_tiles = list(
            self.savegame.tiles.filter(building__building_type__is_wall=True)
            .exclude(wall_hitpoints=None)
            .select_related("building", "building__building_type")
        )

    def get_probability(self) -> int | float:
        wall_tiles_exist = self.savegame.tiles.filter(building__building_type__is_wall=True).exists()
        return super().get_probability() if wall_tiles_exist else 0

    def get_effects(self) -> list:
        return [DamageWall(tile=tile, damage=self.damage) for tile in self.wall_tiles]

    def get_verbose_text(self) -> str:
        count = len(self.wall_tiles)
        return (
            f"A harsh winter has battered the city! "
            f"Frost and ice damaged {count} wall section{'s' if count != 1 else ''}, "
            f"each losing {self.damage} hitpoints."
        )
