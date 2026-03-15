import random

from django.contrib import messages
from django.template.defaultfilters import pluralize

from apps.city.events.effects.building.damage_wall import DamageWall
from apps.city.models import Tile
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 20
    LEVEL = messages.WARNING
    TITLE = "Wall Crumbles"

    affected_tiles: list[Tile]
    damage_per_tile: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.damage_per_tile = random.randint(30, 50)

        eligible_tiles = list(
            self.savegame.tiles.filter(
                building__building_type__is_wall=True,
            )
            .exclude(wall_hitpoints=None)
            .select_related("building", "building__building_type")
        )

        count = random.randint(1, min(3, len(eligible_tiles))) if eligible_tiles else 0
        self.affected_tiles = random.sample(eligible_tiles, count) if count else []

    def get_probability(self) -> int | float:
        wall_tiles_exist = self.savegame.tiles.filter(building__building_type__is_wall=True).exists()
        return super().get_probability() if wall_tiles_exist else 0

    def get_effects(self) -> list:
        return [DamageWall(tile=tile, damage=self.damage_per_tile) for tile in self.affected_tiles]

    def get_verbose_text(self) -> str:
        count = len(self.affected_tiles)
        return (
            f"Sections of your city wall are crumbling! "
            f"{count} wall section{pluralize(count)} suffered {self.damage_per_tile} damage."
        )
