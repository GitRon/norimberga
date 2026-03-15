from apps.city.models import Building, BuildingType, Tile


class DamageWall:
    def __init__(self, *, tile: Tile, damage: int):
        self.tile = tile
        self.damage = damage

    def process(self, *, savegame=None) -> None:
        if self.tile.wall_hitpoints is None:
            return

        self.tile.wall_hitpoints = max(0, self.tile.wall_hitpoints - self.damage)

        if self.tile.wall_hitpoints == 0:
            ruins_type = BuildingType.objects.filter(type=BuildingType.Type.RUINS).first()
            if ruins_type is None:
                raise BuildingType.DoesNotExist("No RUINS BuildingType found. Check that fixtures are loaded.")
            ruins_building = ruins_type.buildings.first()
            if ruins_building is None:
                raise Building.DoesNotExist("No building found for RUINS BuildingType. Check that fixtures are loaded.")
            self.tile.building = ruins_building
            self.tile.wall_hitpoints = None

        self.tile.save()
