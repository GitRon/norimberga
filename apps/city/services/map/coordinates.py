import dataclasses


class MapCoordinatesService:
    map_size: int

    @dataclasses.dataclass(kw_only=True)
    class Coordinates:
        x: int
        y: int

    def __init__(self, map_size: int):
        self.map_size = map_size

    def _get_valid_coordinates(
        self, *, start_x, start_y, min_x: int, max_x: int, min_y: int, max_y: int
    ) -> list[Coordinates]:
        adjacent_coordinates = []
        for iter_x in range(min_x, max_x + 1):
            for iter_y in range(min_y, max_y + 1):
                if iter_x == start_x and iter_y == start_y:
                    continue
                adjacent_coordinates.append(MapCoordinatesService.Coordinates(x=iter_x, y=iter_y))

        return adjacent_coordinates

    def get_adjacent_coordinates(self, x: int, y: int) -> list[Coordinates]:
        min_x = max(0, x - 1)
        max_x = min(x + 1, self.map_size - 1)  # Coordinates start at zero

        min_y = max(0, y - 1)
        max_y = min(y + 1, self.map_size - 1)  # Coordinates start at zero

        return self._get_valid_coordinates(start_x=x, start_y=y, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)

    def get_forward_adjacent_fields(self, x: int, y: int) -> list[Coordinates]:
        """
        Looking from the 0/0 field, get adjacent fields in the "forward" direction
        """
        min_x = x
        max_x = min(x + 1, self.map_size - 1)  # Coordinates start at zero

        min_y = y
        max_y = min(y + 1, self.map_size - 1)  # Coordinates start at zero

        return self._get_valid_coordinates(start_x=x, start_y=y, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)
