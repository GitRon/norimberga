from dataclasses import dataclass

from apps.city.models import Tile
from apps.savegame.models import Savegame


@dataclass(kw_only=True)
class WallCondition:
    tiles: list
    total_hp: int
    total_max_hp: int
    health_percent: int
    total_repair_cost: int


class WallConditionService:
    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> WallCondition:
        tiles = list(
            Tile.objects.filter(savegame=self.savegame, building__building_type__is_wall=True)
            .select_related("building", "building__building_type")
            .order_by("x", "y")
        )
        total_hp = sum(t.wall_hitpoints for t in tiles if t.wall_hitpoints is not None)
        total_max_hp = sum(t.wall_hitpoints_max for t in tiles if t.wall_hitpoints_max is not None)
        health_percent = int(total_hp / total_max_hp * 100) if total_max_hp else 0
        total_repair_cost = sum(t.wall_repair_cost or 0 for t in tiles)
        return WallCondition(
            tiles=tiles,
            total_hp=total_hp,
            total_max_hp=total_max_hp,
            health_percent=health_percent,
            total_repair_cost=total_repair_cost,
        )
