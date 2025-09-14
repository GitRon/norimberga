import pytest

from apps.city.services.map.coordinates import MapCoordinatesService


def test_map_coordinates_service_init():
    """Test MapCoordinatesService initialization."""
    service = MapCoordinatesService(map_size=5)
    assert service.map_size == 5


def test_coordinates_dataclass():
    """Test Coordinates dataclass creation."""
    coords = MapCoordinatesService.Coordinates(x=2, y=3)
    assert coords.x == 2
    assert coords.y == 3


def test_get_valid_coordinates():
    """Test _get_valid_coordinates returns correct coordinates."""
    service = MapCoordinatesService(map_size=5)

    result = service._get_valid_coordinates(
        start_x=1, start_y=1, min_x=0, max_x=2, min_y=0, max_y=2
    )

    # Should return all coordinates in range except start coordinates
    expected_coords = [
        (0, 0), (0, 1), (0, 2),
        (1, 0),         (1, 2),  # (1, 1) excluded as start
        (2, 0), (2, 1), (2, 2)
    ]

    result_coords = [(c.x, c.y) for c in result]
    assert len(result_coords) == 8
    assert set(result_coords) == set(expected_coords)


def test_get_adjacent_coordinates_center():
    """Test get_adjacent_coordinates from center of map."""
    service = MapCoordinatesService(map_size=5)

    result = service.get_adjacent_coordinates(x=2, y=2)

    # Should return 8 adjacent coordinates around (2,2)
    expected_coords = [
        (1, 1), (1, 2), (1, 3),
        (2, 1),         (2, 3),
        (3, 1), (3, 2), (3, 3)
    ]

    result_coords = [(c.x, c.y) for c in result]
    assert len(result_coords) == 8
    assert set(result_coords) == set(expected_coords)
2

def test_get_adjacent_coordinates_corner():
    """Test get_adjacent_coordinates from corner of map."""
    service = MapCoordinatesService(map_size=5)

    result = service.get_adjacent_coordinates(x=0, y=0)

    # Should return 3 adjacent coordinates from (0,0) corner
    expected_coords = [
        (0, 1), (1, 0), (1, 1)
    ]

    result_coords = [(c.x, c.y) for c in result]
    assert len(result_coords) == 3
    assert set(result_coords) == set(expected_coords)


def test_get_adjacent_coordinates_edge():
    """Test get_adjacent_coordinates from edge of map."""
    service = MapCoordinatesService(map_size=5)

    result = service.get_adjacent_coordinates(x=0, y=2)

    # Should return 5 adjacent coordinates from (0,2) edge
    expected_coords = [
        (0, 1), (0, 3),
        (1, 1), (1, 2), (1, 3)
    ]

    result_coords = [(c.x, c.y) for c in result]
    assert len(result_coords) == 5
    assert set(result_coords) == set(expected_coords)


def test_get_forward_adjacent_fields_center():
    """Test get_forward_adjacent_fields from center of map."""
    service = MapCoordinatesService(map_size=5)

    result = service.get_forward_adjacent_fields(x=2, y=2)

    # Should return 3 forward adjacent coordinates
    expected_coords = [
        (2, 3), (3, 2), (3, 3)
    ]

    result_coords = [(c.x, c.y) for c in result]
    assert len(result_coords) == 3
    assert set(result_coords) == set(expected_coords)


def test_get_forward_adjacent_fields_corner():
    """Test get_forward_adjacent_fields from bottom-right corner."""
    service = MapCoordinatesService(map_size=5)

    result = service.get_forward_adjacent_fields(x=4, y=4)

    # Should return 0 coordinates as we're at bottom-right corner
    assert len(result) == 0


def test_get_forward_adjacent_fields_edge():
    """Test get_forward_adjacent_fields from edge."""
    service = MapCoordinatesService(map_size=5)

    result = service.get_forward_adjacent_fields(x=3, y=4)

    # Should return 1 coordinate
    expected_coords = [(4, 4)]

    result_coords = [(c.x, c.y) for c in result]
    assert len(result_coords) == 1
    assert set(result_coords) == set(expected_coords)
