from apps.city.models import Tile


class RemoveBuilding:
    building: Tile

    def __init__(self, tile: Tile):
        self.tile = tile

    def process(self):
        self.tile.building = None
        self.tile.save()
