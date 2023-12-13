from random import randint

from apps.city.models import Savegame, Tile, TileType


class MapGenerationService:
    savegame: Savegame

    def __init__(self, savegame: Savegame):
        self.savegame = savegame

    def get_tile_type(self):
        tile_type = None
        while tile_type is None:
            dice = randint(1, 100)
            tile_type = TileType.objects.filter(probability__gte=dice).order_by("?").first()
        return tile_type

    def process(self):
        # Clear previous map
        self.savegame.tiles.all().delete()

        for x in range(self.savegame.map_size):
            for y in range(self.savegame.map_size):
                Tile.objects.create(savegame=self.savegame, x=x, y=y, tile_type=self.get_tile_type())
