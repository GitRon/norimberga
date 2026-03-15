from dataclasses import dataclass

from django.db.models import QuerySet

from apps.city.constants import MAP_SIZE
from apps.city.models import Tile
from apps.savegame.models import Savegame


@dataclass(kw_only=True)
class WallSegment:
    direction: str
    tiles: list
    total_hp: int
    total_max_hp: int
    hp_ratio: float


class WallSegmentService:
    _CENTER_X = MAP_SIZE / 2 - 0.5
    _CENTER_Y = MAP_SIZE / 2 - 0.5

    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> dict[str, WallSegment]:
        wall_tiles = self._get_wall_tiles()

        by_direction: dict[str, list[Tile]] = {"N": [], "S": [], "E": [], "W": []}
        for tile in wall_tiles:
            direction = self._classify_direction(tile=tile)
            by_direction[direction].append(tile)

        result = {}
        for direction, tiles in by_direction.items():
            total_hp = sum(t.wall_hitpoints for t in tiles if t.wall_hitpoints is not None)
            total_max_hp = sum(t.wall_hitpoints_max for t in tiles if t.wall_hitpoints_max is not None)
            hp_ratio = total_hp / total_max_hp if total_max_hp > 0 else 0.0
            result[direction] = WallSegment(
                direction=direction,
                tiles=tiles,
                total_hp=total_hp,
                total_max_hp=total_max_hp,
                hp_ratio=hp_ratio,
            )

        return result

    def _classify_direction(self, *, tile: Tile) -> str:
        dx = tile.x - self._CENTER_X
        dy = tile.y - self._CENTER_Y

        if abs(dx) > abs(dy):
            return "E" if dx > 0 else "W"
        else:
            return "S" if dy > 0 else "N"

    def _get_wall_tiles(self) -> QuerySet:
        return self.savegame.tiles.filter(wall_hitpoints__isnull=False).select_related(
            "building", "building__building_type"
        )
