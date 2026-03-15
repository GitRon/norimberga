from apps.city.constants import WALL_DECAY_PER_ROUND
from apps.city.events.effects.building.damage_wall import DamageWall
from apps.city.models import Tile
from apps.savegame.models import Savegame


class WallDecayService:
    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> None:
        wall_tiles = Tile.objects.filter(
            savegame=self.savegame,
            building__building_type__is_wall=True,
        ).select_related("building", "building__building_type")

        for tile in wall_tiles:
            DamageWall(tile=tile, damage=WALL_DECAY_PER_ROUND).process()
