from apps.city.models import Building, Tile


class RemoveBuilding:
    building: Tile

    def __init__(self, *, tile: Tile):
        self.tile = tile

    def process(self, *, savegame=None):
        # Replace the building with ruins instead of removing it entirely
        # This ensures that damaged buildings leave ruins that need to be demolished
        ruins = Building.objects.get(pk=28)  # Ruins building (pk=28)
        self.tile.building = ruins
        self.tile.save()
