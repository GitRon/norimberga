from unittest import mock

import pytest

from apps.city.managers.tile import TileManager, TileQuerySet
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TileFactory,
)
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_tile_queryset_filter_savegame():
    """Test filter_savegame returns tiles for specific savegame."""
    savegame1 = SavegameFactory()
    savegame2 = SavegameFactory()

    tile1 = TileFactory(savegame=savegame1)
    tile2 = TileFactory(savegame=savegame1)
    tile3 = TileFactory(savegame=savegame2)

    # Test filtering by savegame1
    queryset = TileQuerySet(model=tile1.__class__)
    result = queryset.filter_savegame(savegame=savegame1)

    # Should only return tiles from savegame1
    tile_ids = list(result.values_list("id", flat=True))
    assert tile1.id in tile_ids
    assert tile2.id in tile_ids
    assert tile3.id not in tile_ids


@pytest.mark.django_db
def test_tile_queryset_filter_adjacent_tiles():
    """Test filter_adjacent_tiles returns adjacent tiles."""
    savegame = SavegameFactory()

    # Create a 3x3 grid of tiles
    center_tile = TileFactory(savegame=savegame, x=1, y=1)
    adjacent_tiles = [
        TileFactory(savegame=savegame, x=0, y=0),
        TileFactory(savegame=savegame, x=0, y=1),
        TileFactory(savegame=savegame, x=0, y=2),
        TileFactory(savegame=savegame, x=1, y=0),
        TileFactory(savegame=savegame, x=1, y=2),
        TileFactory(savegame=savegame, x=2, y=0),
        TileFactory(savegame=savegame, x=2, y=1),
        TileFactory(savegame=savegame, x=2, y=2),
    ]
    # Non-adjacent tile
    far_tile = TileFactory(savegame=savegame, x=5, y=5)

    queryset = TileQuerySet(model=center_tile.__class__)

    # Mock MapCoordinatesService to return expected adjacent coordinates
    with mock.patch("apps.city.managers.tile.MapCoordinatesService") as mock_service_class:
        mock_service = mock_service_class.return_value

        # Mock the adjacent coordinates
        mock_coords = [
            mock.Mock(x=0, y=0),
            mock.Mock(x=0, y=1),
            mock.Mock(x=0, y=2),
            mock.Mock(x=1, y=0),
            mock.Mock(x=1, y=2),
            mock.Mock(x=2, y=0),
            mock.Mock(x=2, y=1),
            mock.Mock(x=2, y=2),
        ]
        mock_service.get_adjacent_coordinates.return_value = mock_coords

        result = queryset.filter_adjacent_tiles(tile=center_tile)

        # Verify service was called correctly
        mock_service_class.assert_called_once_with()
        mock_service.get_adjacent_coordinates.assert_called_once_with(x=center_tile.x, y=center_tile.y)

        # The result should contain the adjacent tiles
        result_ids = set(result.values_list("id", flat=True))
        expected_ids = {t.id for t in adjacent_tiles}

        # Should contain all adjacent tiles but not the far tile or center tile
        assert expected_ids.issubset(result_ids)
        assert far_tile.id not in result_ids
        assert center_tile.id not in result_ids


@pytest.mark.django_db
def test_tile_queryset_filter_city_building():
    """Test filter_city_building returns tiles with city buildings."""
    # Create building types
    city_building_type = BuildingTypeFactory(is_city=True)
    country_building_type = BuildingTypeFactory(is_city=False, is_country=True)

    # Create buildings
    city_building = BuildingFactory(building_type=city_building_type)
    country_building = BuildingFactory(building_type=country_building_type)

    # Create tiles
    tile_with_city_building = TileFactory(building=city_building)
    tile_with_country_building = TileFactory(building=country_building)
    tile_without_building = TileFactory(building=None)

    queryset = TileQuerySet(model=tile_with_city_building.__class__)
    result = queryset.filter_city_building()

    result_ids = list(result.values_list("id", flat=True))

    # Should only return tile with city building
    assert tile_with_city_building.id in result_ids
    assert tile_with_country_building.id not in result_ids
    assert tile_without_building.id not in result_ids


@pytest.mark.django_db
def test_tile_queryset_chaining():
    """Test queryset methods can be chained together."""
    savegame = SavegameFactory()

    # Create city building type
    city_building_type = BuildingTypeFactory(is_city=True)
    city_building = BuildingFactory(building_type=city_building_type)

    # Create center tile with city building
    center_tile = TileFactory(savegame=savegame, x=1, y=1, building=city_building)

    # Create adjacent tile with city building
    adjacent_city_tile = TileFactory(savegame=savegame, x=0, y=0, building=city_building)

    # Create adjacent tile without city building
    adjacent_non_city_tile = TileFactory(savegame=savegame, x=0, y=1, building=None)

    # Create non-adjacent tile with city building
    far_city_tile = TileFactory(savegame=savegame, x=2, y=2, building=city_building)

    queryset = TileQuerySet(model=center_tile.__class__)

    with mock.patch("apps.city.managers.tile.MapCoordinatesService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_coords = [
            mock.Mock(x=0, y=0),
            mock.Mock(x=0, y=1),
            mock.Mock(x=0, y=2),
            mock.Mock(x=1, y=0),
            mock.Mock(x=1, y=2),
            mock.Mock(x=2, y=0),
            mock.Mock(x=2, y=1),
        ]
        mock_service.get_adjacent_coordinates.return_value = mock_coords

        # Chain methods: filter by savegame, then adjacent tiles, then city buildings
        result = (
            queryset.filter_savegame(savegame=savegame).filter_adjacent_tiles(tile=center_tile).filter_city_building()
        )

        result_ids = list(result.values_list("id", flat=True))

        # Should only return adjacent tile with city building
        assert adjacent_city_tile.id in result_ids
        assert adjacent_non_city_tile.id not in result_ids
        assert far_city_tile.id not in result_ids
        assert center_tile.id not in result_ids


def test_tile_manager_from_queryset():
    """Test TileManager is created from TileQuerySet."""
    # Verify that TileManager inherits from the queryset methods
    manager = TileManager()

    # Should have queryset methods
    assert hasattr(manager, "filter_savegame")
    assert hasattr(manager, "filter_adjacent_tiles")
    assert hasattr(manager, "filter_city_building")


@pytest.mark.django_db
def test_tile_manager_integration():
    """Test TileManager works with actual model queries."""
    from apps.city.models import Tile

    savegame = SavegameFactory()
    city_building_type = BuildingTypeFactory(is_city=True)
    city_building = BuildingFactory(building_type=city_building_type)

    tile = TileFactory(savegame=savegame, building=city_building)

    # Test manager methods work on actual model
    result = Tile.objects.filter_savegame(savegame=savegame)
    assert tile in result

    result = Tile.objects.filter_city_building()
    assert tile in result


@pytest.mark.django_db
def test_tile_queryset_filter_adjacent_tiles_edge_case():
    """Test filter_adjacent_tiles with edge coordinates."""
    savegame = SavegameFactory()

    # Create tile at edge
    edge_tile = TileFactory(savegame=savegame, x=0, y=0)

    queryset = TileQuerySet(model=edge_tile.__class__)

    with mock.patch("apps.city.managers.tile.MapCoordinatesService") as mock_service_class:
        mock_service = mock_service_class.return_value

        # Mock coordinates for edge case (should have fewer adjacent coordinates)
        mock_coords = [mock.Mock(x=0, y=1), mock.Mock(x=1, y=0), mock.Mock(x=1, y=1)]
        mock_service.get_adjacent_coordinates.return_value = mock_coords

        result = queryset.filter_adjacent_tiles(tile=edge_tile)

        # Verify service was called with correct parameters
        mock_service_class.assert_called_once_with()
        mock_service.get_adjacent_coordinates.assert_called_once_with(x=0, y=0)

        # Result should be filtered by the mock coordinates
        # This test mainly verifies the integration works correctly
        assert result is not None


@pytest.mark.django_db
def test_tile_queryset_filter_city_building_edge_cases():
    """Test filter_city_building with various building type combinations."""
    # Create building types with different combinations
    city_only = BuildingTypeFactory(is_city=True, is_country=False)
    country_only = BuildingTypeFactory(is_city=False, is_country=True)
    both = BuildingTypeFactory(is_city=True, is_country=True)
    neither = BuildingTypeFactory(is_city=False, is_country=False)

    # Create buildings and tiles
    tile_city_only = TileFactory(building=BuildingFactory(building_type=city_only))
    tile_country_only = TileFactory(building=BuildingFactory(building_type=country_only))
    tile_both = TileFactory(building=BuildingFactory(building_type=both))
    tile_neither = TileFactory(building=BuildingFactory(building_type=neither))

    queryset = TileQuerySet(model=tile_city_only.__class__)
    result = queryset.filter_city_building()

    result_ids = set(result.values_list("id", flat=True))

    # Should include tiles with is_city=True (city_only and both)
    assert tile_city_only.id in result_ids
    assert tile_both.id in result_ids

    # Should exclude tiles with is_city=False (country_only and neither)
    assert tile_country_only.id not in result_ids
    assert tile_neither.id not in result_ids


@pytest.mark.django_db
def test_tile_manager_has_adjacent_city_building_true():
    """Test has_adjacent_city_building returns True when adjacent city building exists."""
    savegame = SavegameFactory()
    city_building_type = BuildingTypeFactory(is_city=True)
    city_building = BuildingFactory(building_type=city_building_type)

    # Create tile with city building at adjacent coordinates
    TileFactory(savegame=savegame, x=0, y=0, building=city_building)

    # Create tile to test
    tile = TileFactory(savegame=savegame, x=1, y=1)

    # Mock MapCoordinatesService to return adjacent coordinates
    with mock.patch("apps.city.managers.tile.MapCoordinatesService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_coords = [
            mock.Mock(x=0, y=0),
            mock.Mock(x=0, y=1),
            mock.Mock(x=0, y=2),
            mock.Mock(x=1, y=0),
            mock.Mock(x=1, y=2),
            mock.Mock(x=2, y=0),
            mock.Mock(x=2, y=1),
            mock.Mock(x=2, y=2),
        ]
        mock_service.get_adjacent_coordinates.return_value = mock_coords

        from apps.city.models import Tile

        result = Tile.objects.has_adjacent_city_building(tile=tile)

        assert result is True
        mock_service_class.assert_called_once_with()
        mock_service.get_adjacent_coordinates.assert_called_once_with(x=tile.x, y=tile.y)


@pytest.mark.django_db
def test_tile_manager_has_adjacent_city_building_false():
    """Test has_adjacent_city_building returns False when no adjacent city building exists."""
    savegame = SavegameFactory()

    # Create tile without adjacent city buildings
    tile = TileFactory(savegame=savegame, x=1, y=1)

    # Create a non-city building
    country_building_type = BuildingTypeFactory(is_city=False, is_country=True)
    country_building = BuildingFactory(building_type=country_building_type)

    # Create adjacent tile with non-city building
    TileFactory(savegame=savegame, x=0, y=0, building=country_building)

    with mock.patch("apps.city.managers.tile.MapCoordinatesService") as mock_service_class:
        mock_service = mock_service_class.return_value
        mock_coords = [
            mock.Mock(x=0, y=0),
            mock.Mock(x=0, y=1),
            mock.Mock(x=0, y=2),
            mock.Mock(x=1, y=0),
            mock.Mock(x=1, y=2),
            mock.Mock(x=2, y=0),
            mock.Mock(x=2, y=1),
            mock.Mock(x=2, y=2),
        ]
        mock_service.get_adjacent_coordinates.return_value = mock_coords

        from apps.city.models import Tile

        result = Tile.objects.has_adjacent_city_building(tile=tile)

        assert result is False
