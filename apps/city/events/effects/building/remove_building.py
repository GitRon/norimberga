from apps.city.models import BuildingType, Tile


class RemoveBuilding:
    building: Tile

    def __init__(self, *, tile: Tile):
        self.tile = tile

    def process(self, *, savegame=None):
        # Replace the building with ruins instead of removing it entirely
        # This ensures that damaged buildings leave ruins that need to be demolished
        ruins_type = BuildingType.objects.get(type=BuildingType.Type.RUINS)
        ruins = ruins_type.buildings.first()
        self.tile.building = ruins
        self.tile.save()
