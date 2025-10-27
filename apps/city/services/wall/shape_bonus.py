from apps.city.models import Tile
from apps.savegame.models import Savegame


class WallShapeBonusService:
    """
    Service to calculate defense bonus based on wall shape quality.

    Awards bonus points for walls that form smooth, well-connected shapes.
    Wall tiles with exactly 2 orthogonal neighbors are considered "smooth"
    (forming either straight lines or 90-degree corners).

    Algorithm:
    1. Get all wall tiles
    2. For each wall, count orthogonal (non-diagonal) wall neighbors
    3. Award bonus for walls with exactly 2 neighbors (smooth configuration)
    4. Return total bonus points
    """

    SMOOTH_WALL_BONUS = 5  # Bonus points per smooth wall tile

    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> int:
        """
        Calculate the shape bonus for wall configuration.

        Returns:
            Bonus defense points based on wall shape quality
        """
        wall_tiles = self._get_wall_tiles()

        if not wall_tiles:
            return 0

        smooth_wall_count = 0

        for tile in wall_tiles:
            orthogonal_wall_neighbors = self._count_orthogonal_wall_neighbors(tile=tile)

            # Award bonus for tiles with exactly 2 neighbors (smooth walls/corners)
            if orthogonal_wall_neighbors == 2:
                smooth_wall_count += 1

        return smooth_wall_count * self.SMOOTH_WALL_BONUS

    def _get_wall_tiles(self) -> list[Tile]:
        """Get all tiles with wall buildings."""
        return list(
            Tile.objects.filter(savegame=self.savegame, building__building_type__is_wall=True).select_related(
                "building", "building__building_type"
            )
        )

    def _count_orthogonal_wall_neighbors(self, *, tile: Tile) -> int:
        """
        Count how many orthogonal neighbors of this tile are also walls.

        Only checks up, down, left, right (not diagonals).
        """
        orthogonal_offsets = [
            (0, 1),  # up
            (0, -1),  # down
            (1, 0),  # right
            (-1, 0),  # left
        ]

        wall_neighbor_count = 0

        for dx, dy in orthogonal_offsets:
            neighbor_x = tile.x + dx
            neighbor_y = tile.y + dy

            try:
                neighbor_tile = Tile.objects.select_related("building", "building__building_type").get(
                    savegame=self.savegame, x=neighbor_x, y=neighbor_y
                )

                if neighbor_tile.building and neighbor_tile.building.building_type.is_wall:
                    wall_neighbor_count += 1

            except Tile.DoesNotExist:
                continue

        return wall_neighbor_count
