import dataclasses
import typing

if typing.TYPE_CHECKING:
    from apps.city.models import Tile


class MapCoordinatesService:
    @dataclasses.dataclass
    class Coordinates:
        x: int
        y: int

    @staticmethod
    def get_adjacent_coordinates(tile: "Tile") -> list[Coordinates]:
        x = tile.x
        y = tile.y

        min_x = max(0, x - 1)
        max_x = min(x + 1, tile.savegame.map_size - 1)  # Coordinates start at zero

        min_y = max(0, y - 1)
        max_y = min(y + 1, tile.savegame.map_size - 1)  # Coordinates start at zero

        adjacent_coordinates = []
        for iter_x in range(min_x, max_x + 1):
            for iter_y in range(min_y, max_y + 1):
                if iter_x == x and iter_y == y:
                    continue
                adjacent_coordinates.append(MapCoordinatesService.Coordinates(x=iter_x, y=iter_y))

        return adjacent_coordinates
