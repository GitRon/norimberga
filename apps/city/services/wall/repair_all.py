from django.db import transaction

from apps.city.models import Tile
from apps.savegame.models import Savegame


class WallRepairAllService:
    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> None:
        tiles = self._get_damaged_wall_tiles()
        if not tiles:
            return

        total_cost = sum(t.wall_repair_cost or 0 for t in tiles)

        if self.savegame.coins < total_cost:
            raise ValueError(f"Not enough coins. Repair costs {total_cost} coins.")

        with transaction.atomic():
            for tile in tiles:
                tile.wall_hitpoints = tile.wall_hitpoints_max

            Tile.objects.bulk_update(tiles, ["wall_hitpoints"])

            self.savegame.coins -= total_cost
            self.savegame.save()

    def _get_damaged_wall_tiles(self) -> list:
        tiles = list(
            Tile.objects.filter(savegame=self.savegame, building__building_type__is_wall=True)
            .exclude(wall_hitpoints=None)
            .select_related("building", "building__building_type")
        )
        return [t for t in tiles if t.wall_repair_cost]
