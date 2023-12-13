from city.models import Savegame, Tile, TileType


class MapGenerationService:
    savegame: Savegame

    def __init__(self, savegame: Savegame):
        self.savegame = savegame

    def process(self):

        for x in range(self.savegame.map_size):
            for y in range(self.savegame.map_size):
                Tile.objects.create(savegame=self.savegame, x=x, y=y, tile_type=TileType.objects.all().order_by("?").first())
