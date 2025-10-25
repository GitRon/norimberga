from apps.city.models import Tile
from apps.city.services.map.coordinates import MapCoordinatesService
from apps.savegame.models import Savegame


class WallEnclosureService:
    """
    Service to detect if all city buildings are enclosed by walls.

    Only wall buildings count as barriers. Water terrain does NOT act as a wall.
    If there is a gap with water, the wall is not considered enclosed.

    Algorithm:
    1. Find a city building (preferably unique building as starting point)
    2. Mark all adjacent tiles that are not walls (including water tiles)
    3. Repeat for all marked tiles until no new tiles can be marked
    4. If any marked tile reaches the map edge, the city is not enclosed
    5. If any city building is not reachable, it's outside the enclosure
    """

    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame
        self.map_service = MapCoordinatesService()

    def process(self) -> bool:
        """
        Check if the city is enclosed by walls.
        """
        # Get all city building tiles
        city_tiles = self._get_city_building_tiles()

        if not city_tiles:
            # No city buildings means not enclosed
            return False

        # Start from a city building (preferably unique)
        start_tile = self._get_starting_tile(city_tiles=city_tiles)

        # Perform flood fill to find all reachable non-wall tiles
        reachable_tiles = self._flood_fill(start_tile=start_tile)

        # Check if we reached the edge of the map
        if self._reached_map_edge(tiles=reachable_tiles):
            return False

        # Check if all city buildings are reachable
        city_tile_ids = {tile.id for tile in city_tiles}
        reachable_tile_ids = {tile.id for tile in reachable_tiles}

        # All city buildings must be in the reachable set
        return city_tile_ids.issubset(reachable_tile_ids)

    def _get_city_building_tiles(self) -> list[Tile]:
        """Get all tiles with city buildings (excluding walls)."""
        return list(
            Tile.objects.filter(savegame=self.savegame, building__building_type__is_city=True)
            .exclude(building__building_type__is_wall=True)
            .select_related("building", "building__building_type")
        )

    def _get_starting_tile(self, *, city_tiles: list[Tile]) -> Tile:
        """Get a starting tile for the flood fill (prefer unique buildings)."""
        for tile in city_tiles:
            if tile.building and tile.building.building_type.is_unique:
                return tile
        return city_tiles[0]

    def _flood_fill(self, *, start_tile: Tile) -> list[Tile]:
        """
        Perform flood fill from start_tile, marking all reachable non-wall tiles.
        """
        visited = set()
        to_visit = [start_tile]
        reachable = []

        while to_visit:
            current_tile = to_visit.pop(0)

            # Skip if already visited
            tile_key = (current_tile.x, current_tile.y)
            if tile_key in visited:
                continue

            visited.add(tile_key)
            reachable.append(current_tile)

            # Get adjacent tiles
            adjacent_coords = self.map_service.get_adjacent_coordinates(x=current_tile.x, y=current_tile.y)

            for coord in adjacent_coords:
                coord_key = (coord.x, coord.y)
                if coord_key in visited:
                    continue

                # Get the tile at this coordinate
                try:
                    adjacent_tile = Tile.objects.select_related("building", "building__building_type").get(
                        savegame=self.savegame, x=coord.x, y=coord.y
                    )

                    # Only add non-wall tiles to the queue
                    if not self._is_wall(tile=adjacent_tile):
                        to_visit.append(adjacent_tile)

                except Tile.DoesNotExist:
                    continue

        return reachable

    def _is_wall(self, *, tile: Tile) -> bool:
        """Check if a tile has a wall building."""
        return tile.building is not None and tile.building.building_type.is_wall

    def _reached_map_edge(self, *, tiles: list[Tile]) -> bool:
        """Check if any of the tiles are at the edge of the map."""
        return any(tile.is_edge_tile() for tile in tiles)
