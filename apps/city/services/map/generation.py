import random
from random import randint

from apps.city.models import Building, BuildingType, Savegame, Terrain, Tile
from apps.city.services.map.coordinates import MapCoordinatesService

# Number of random country buildings to place on the map during generation
INITIAL_COUNTRY_BUILDINGS = 3


class MapGenerationService:
    savegame: Savegame

    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def get_terrain(self) -> Terrain:
        terrain = None
        while terrain is None:
            dice = randint(1, 100)
            terrain = Terrain.objects.filter(probability__gte=dice).exclude(name="River").order_by("?").first()
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
        terrain_river = Terrain.objects.filter(name="River").first()
        if not terrain_river:
            raise ValueError("River terrain not found. Please ensure River terrain exists in the database.")

        iter_coordinates = start_coordinates
        while iter_coordinates:
            # Create river tile
            Tile.objects.filter_savegame(savegame=self.savegame).filter(
                x=iter_coordinates.x, y=iter_coordinates.y
            ).update(terrain=terrain_river)

            # If we have reached the other end of the map, we are done
            if iter_coordinates.x == self.savegame.map_size - 1 or iter_coordinates.y == self.savegame.map_size - 1:
                break

            # Get the next field which should become a river
            service = MapCoordinatesService(map_size=self.savegame.map_size)
            forward_adjacent_fields = service.get_forward_adjacent_fields(x=iter_coordinates.x, y=iter_coordinates.y)
            iter_coordinates = random.choice(forward_adjacent_fields)

    def _place_random_country_buildings(self) -> None:
        """
        Place random country buildings on the map at valid locations.
        All buildings are placed at level 1.
        Buildings cannot be placed on edge tiles.
        """
        # Get all country building types that have allowed terrains
        country_building_types = BuildingType.objects.filter(is_country=True).prefetch_related("allowed_terrains")

        if not country_building_types.exists():
            return

        # Get all non-edge tiles that could potentially have buildings
        tiles = list(self.savegame.tiles.select_related("terrain").all())
        # Filter out edge tiles
        tiles = [t for t in tiles if not t.is_edge_tile()]

        if not tiles:
            return

        placed_count = 0
        attempts = 0
        max_attempts = len(tiles) * 2  # Prevent infinite loops

        while placed_count < INITIAL_COUNTRY_BUILDINGS and attempts < max_attempts:
            attempts += 1

            # Pick a random tile
            tile = random.choice(tiles)

            # Skip if tile already has a building
            if tile.building:
                continue

            # Get building types that can be placed on this terrain
            valid_building_types = [bt for bt in country_building_types if tile.terrain in bt.allowed_terrains.all()]

            if not valid_building_types:
                continue

            # Pick a random valid building type
            building_type = random.choice(valid_building_types)

            # Get level 1 building for this type
            building = Building.objects.filter(building_type=building_type, level=1).first()

            if not building:
                continue

            # Place the building on the tile
            tile.building = building
            tile.save(update_fields=["building"])

            placed_count += 1

    def process(self):
        # Clear previous map
        self.savegame.tiles.all().delete()

        # Generate map
        for x in range(self.savegame.map_size):
            for y in range(self.savegame.map_size):
                Tile.objects.create(savegame=self.savegame, x=x, y=y, terrain=self.get_terrain())

        # Draw river
        self._draw_river()

        # Place random country buildings
        self._place_random_country_buildings()
