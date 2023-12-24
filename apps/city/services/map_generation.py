from random import randint

from apps.city.models import Savegame, Terrain, Tile


class MapGenerationService:
    savegame: Savegame

    def __init__(self, savegame: Savegame):
        self.savegame = savegame

    def get_terrain(self):
        terrain = None
        while terrain is None:
            dice = randint(1, 100)
            terrain = Terrain.objects.filter(probability__gte=dice).order_by("?").first()
        return terrain

    def process(self):
        # Clear previous map
        self.savegame.tiles.all().delete()

        for x in range(self.savegame.map_size):
            for y in range(self.savegame.map_size):
                Tile.objects.create(savegame=self.savegame, x=x, y=y, terrain=self.get_terrain())
