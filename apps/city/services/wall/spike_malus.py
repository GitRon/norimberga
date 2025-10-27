from apps.city.models import Tile
from apps.savegame.models import Savegame


class WallSpikeMalusService:
    """
    Service to calculate defense malus based on wall spikes.

    Penalizes wall tiles with 0-1 orthogonal neighbors (spikes or isolated walls).
    These configurations are structurally weak and vulnerable.

    Algorithm:
    1. Get all wall tiles
    2. For each wall, count orthogonal (non-diagonal) wall neighbors
    3. Apply malus for walls with 0-1 neighbors (spike configuration)
    4. Return total malus points (as a negative value)
    """

    SPIKE_MALUS = -10  # Malus points per spike wall tile (negative)

    def __init__(self, *, savegame: Savegame):
        self.savegame = savegame

    def process(self) -> int:
        """
        Calculate the spike malus for wall configuration.

        Returns:
            Malus defense points (negative value) based on spike count
        """
        wall_tiles = self._get_wall_tiles()

        if not wall_tiles:
            return 0

        spike_count = 0

        for tile in wall_tiles:
            orthogonal_wall_neighbors = self._count_orthogonal_wall_neighbors(tile=tile)

            # Apply malus for tiles with 0-1 neighbors (spikes)
            if orthogonal_wall_neighbors <= 1:
                spike_count += 1

        return spike_count * self.SPIKE_MALUS

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
