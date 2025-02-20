import random
from random import randint

from apps.city.models import Savegame, Terrain, Tile
from apps.city.services.map.coordinates import MapCoordinatesService


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

    def _draw_river(self):
        """
        Draw a river
        Attention: We don't let the river start at 0/0 to avoid odd behaviour
        """
        dice = randint(1, 2)
        # Decide if the river starts on the x- or y-axis
        if dice == 1:
            start_coordinates = MapCoordinatesService.Coordinates(x=0, y=randint(1, self.savegame.map_size - 1))
        else:
            start_coordinates = MapCoordinatesService.Coordinates(x=randint(1, self.savegame.map_size - 1), y=0)

        # Fetch river terrain
        # TODO(RV): differentiate between lake and river?
        terrain_water = Terrain.objects.get(name="River")

        iter_coordinates = start_coordinates
        while iter_coordinates:
            # Create river tile
            Tile.objects.filter_savegame(savegame=self.savegame).filter(
                x=iter_coordinates.x, y=iter_coordinates.y
            ).update(terrain=terrain_water)

            # If we have reached the other end of the map, we are done
            if iter_coordinates.x == self.savegame.map_size - 1 or iter_coordinates.y == self.savegame.map_size - 1:
                break

            # Get the next field which should become a river
            service = MapCoordinatesService(map_size=self.savegame.map_size)
            forward_adjacent_fields = service.get_forward_adjacent_fields(x=iter_coordinates.x, y=iter_coordinates.y)
            iter_coordinates = random.choice(forward_adjacent_fields)

    def process(self):
        # Clear previous map
        self.savegame.tiles.all().delete()

        # Generate map
        for x in range(self.savegame.map_size):
            for y in range(self.savegame.map_size):
                Tile.objects.create(savegame=self.savegame, x=x, y=y, terrain=self.get_terrain())

        # Draw river
        self._draw_river()
