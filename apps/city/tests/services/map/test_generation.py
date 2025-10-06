from unittest import mock

import pytest

from apps.city.services.map.coordinates import MapCoordinatesService
from apps.city.services.map.generation import INITIAL_COUNTRY_BUILDINGS, MapGenerationService
from apps.city.tests.factories import (
    BuildingFactory,
    CountryBuildingTypeFactory,
    RiverTerrainFactory,
    SavegameFactory,
    TerrainFactory,
    TileFactory,
)


@pytest.mark.django_db
def test_map_generation_service_init():
    """Test MapGenerationService initialization."""
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame)

    assert service.savegame == savegame


@pytest.mark.django_db
def test_map_generation_service_get_terrain():
    """Test get_terrain returns terrain based on probability."""
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame)

    # Create terrains with different probabilities
    terrain1 = TerrainFactory(name="Forest", probability=50)
    terrain2 = TerrainFactory(name="Plains", probability=80)

    with mock.patch("apps.city.services.map.generation.randint") as mock_randint:
        mock_randint.return_value = 60  # Should match terrain2 (probability 80)

        result = service.get_terrain()

        # Should return terrain2 as its probability (80) >= dice (60)
        assert result in [terrain1, terrain2]


@pytest.mark.django_db
def test_map_generation_service_get_terrain_retry():
    """Test get_terrain retries until finding valid terrain."""
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame)

    terrain = TerrainFactory(name="Forest", probability=50)

    with mock.patch("apps.city.services.map.generation.randint") as mock_randint:
        # First call returns 10 (no terrain matches), second call returns 60 (matches)
        mock_randint.side_effect = [10, 60]

        # Mock the terrain queryset to return None first, then terrain
        with mock.patch("apps.city.models.Terrain.objects.filter") as mock_filter:
            mock_queryset = mock.Mock()
            mock_filter.return_value = mock_queryset
            mock_queryset.exclude.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_queryset
            mock_queryset.first.side_effect = [None, terrain]

            result = service.get_terrain()

            assert result == terrain
            assert mock_randint.call_count == 2


@pytest.mark.django_db
def test_map_generation_service_draw_river_y_axis():
    """Test _draw_river creates river tiles starting from y-axis."""
    savegame = SavegameFactory(map_size=3)
    service = MapGenerationService(savegame=savegame)

    # Clear any existing water terrains and create a unique one
    from apps.city.models import Terrain

    Terrain.objects.filter(is_water=True).delete()
    river_terrain = RiverTerrainFactory()

    # Create initial tiles
    for x in range(3):
        for y in range(3):
            TileFactory(savegame=savegame, x=x, y=y)

    with (
        mock.patch("apps.city.services.map.generation.randint") as mock_randint,
        mock.patch("apps.city.services.map.generation.random.choice") as mock_choice,
    ):
        # Set up river starting at (0, 1) and going to (1, 1), then (2, 2)
        mock_randint.side_effect = [1, 1]  # dice=1 means start on y-axis, y=1

        # Mock coordinate choices for river path
        coord1 = MapCoordinatesService.Coordinates(x=1, y=1)
        coord2 = MapCoordinatesService.Coordinates(x=2, y=2)
        mock_choice.side_effect = [coord1, coord2]

        service._draw_river()

        # Verify river tiles were created at expected coordinates
        river_tiles = savegame.tiles.filter(terrain=river_terrain)
        assert river_tiles.count() >= 1


@pytest.mark.django_db
def test_map_generation_service_draw_river_x_axis():
    """Test _draw_river creates river tiles starting from x-axis."""
    savegame = SavegameFactory(map_size=3)
    service = MapGenerationService(savegame=savegame)

    # Clear any existing water terrains and create a unique one
    from apps.city.models import Terrain

    Terrain.objects.filter(is_water=True).delete()
    river_terrain = RiverTerrainFactory()

    # Create initial tiles
    for x in range(3):
        for y in range(3):
            TileFactory(savegame=savegame, x=x, y=y)

    with (
        mock.patch("apps.city.services.map.generation.randint") as mock_randint,
        mock.patch("apps.city.services.map.generation.random.choice") as mock_choice,
    ):
        # Set up river starting on x-axis - dice=2 triggers else branch (line 31)
        mock_randint.side_effect = [2, 1]  # dice=2 means start on x-axis, x=1

        # Mock coordinate choices for river path
        coord1 = MapCoordinatesService.Coordinates(x=1, y=1)
        coord2 = MapCoordinatesService.Coordinates(x=2, y=2)
        mock_choice.side_effect = [coord1, coord2]

        service._draw_river()

        # Verify river tiles were created at expected coordinates
        river_tiles = savegame.tiles.filter(terrain=river_terrain)
        assert river_tiles.count() >= 1


@pytest.mark.django_db
def test_map_generation_service_draw_river_missing_terrain():
    """Test _draw_river raises ValueError when River terrain is missing."""
    savegame = SavegameFactory(map_size=3)
    service = MapGenerationService(savegame=savegame)

    # Clear any existing water terrains to simulate missing terrain
    from apps.city.models import Terrain

    Terrain.objects.filter(is_water=True).delete()

    # Create initial tiles
    for x in range(3):
        for y in range(3):
            TileFactory(savegame=savegame, x=x, y=y)

    with pytest.raises(
        ValueError,
        match=r"River terrain not found\. Please ensure River terrain exists in the database\.",
    ):
        service._draw_river()


@pytest.mark.django_db
def test_map_generation_service_process():
    """Test process method creates complete map with river."""
    savegame = SavegameFactory(map_size=3)
    service = MapGenerationService(savegame=savegame)

    terrain = TerrainFactory()
    RiverTerrainFactory()

    with (
        mock.patch.object(service, "get_terrain") as mock_get_terrain,
        mock.patch.object(service, "_draw_river") as mock_draw_river,
    ):
        mock_get_terrain.return_value = terrain

        service.process()

        # Verify all tiles were created
        assert savegame.tiles.count() == 9  # 3x3 map

        # Verify draw_river was called
        mock_draw_river.assert_called_once()

        # Verify get_terrain was called for each tile
        assert mock_get_terrain.call_count == 9


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings():
    """Test _place_random_country_buildings places buildings on valid tiles."""
    savegame = SavegameFactory(map_size=5)
    service = MapGenerationService(savegame=savegame)

    # Create terrains
    terrain_grass = TerrainFactory(name="Grass", probability=80)
    terrain_forest = TerrainFactory(name="Forest", probability=60)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain_grass, terrain_forest])

    # Create level 1 building for this type
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles with different terrains
    for x in range(5):
        for y in range(5):
            terrain = terrain_grass if (x + y) % 2 == 0 else terrain_forest
            TileFactory(savegame=savegame, x=x, y=y, terrain=terrain)

    service._place_random_country_buildings()

    # Verify that buildings were placed
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == INITIAL_COUNTRY_BUILDINGS

    # Verify all buildings are level 1
    for tile in tiles_with_buildings:
        assert tile.building.level == 1
        assert tile.building.building_type.is_country is True


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_no_building_types():
    """Test _place_random_country_buildings does nothing when no country building types exist."""
    savegame = SavegameFactory(map_size=3)
    service = MapGenerationService(savegame=savegame)

    terrain = TerrainFactory()

    # Create tiles without any country building types
    for x in range(3):
        for y in range(3):
            TileFactory(savegame=savegame, x=x, y=y, terrain=terrain)

    service._place_random_country_buildings()

    # Verify no buildings were placed
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_no_valid_terrains():
    """Test _place_random_country_buildings handles case where buildings can't be placed."""
    savegame = SavegameFactory(map_size=3)
    service = MapGenerationService(savegame=savegame)

    # Create terrain that won't be allowed for country buildings
    terrain_water = TerrainFactory(name="Water", is_water=True)

    # Create country building type that doesn't allow water terrain
    terrain_grass = TerrainFactory(name="Grass")
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain_grass])
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles with only water terrain (which isn't allowed)
    for x in range(3):
        for y in range(3):
            TileFactory(savegame=savegame, x=x, y=y, terrain=terrain_water)

    service._place_random_country_buildings()

    # Verify no buildings were placed because no valid terrains available
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0


@pytest.mark.django_db
def test_map_generation_service_process_includes_country_buildings():
    """Test process method includes country building placement."""
    savegame = SavegameFactory(map_size=5)
    service = MapGenerationService(savegame=savegame)

    terrain = TerrainFactory()
    RiverTerrainFactory()

    # Create country building setup
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])
    BuildingFactory(building_type=country_building_type, level=1)

    with (
        mock.patch.object(service, "get_terrain") as mock_get_terrain,
        mock.patch.object(service, "_draw_river"),
        mock.patch.object(service, "_place_random_country_buildings") as mock_place_buildings,
    ):
        mock_get_terrain.return_value = terrain

        service.process()

        # Verify _place_random_country_buildings was called
        mock_place_buildings.assert_called_once()


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_excludes_edge_tiles():
    """Test _place_random_country_buildings does not place buildings on edge tiles."""
    savegame = SavegameFactory(map_size=5)
    service = MapGenerationService(savegame=savegame)

    # Create terrain
    terrain = TerrainFactory(name="Grass", probability=80)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])

    # Create level 1 building for this type
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles - all with same terrain
    for x in range(5):
        for y in range(5):
            TileFactory(savegame=savegame, x=x, y=y, terrain=terrain)

    service._place_random_country_buildings()

    # Verify that buildings were placed
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == INITIAL_COUNTRY_BUILDINGS

    # Verify none of the buildings are on edge tiles
    for tile in tiles_with_buildings:
        assert tile.is_edge_tile() is False
        assert tile.x != 0
        assert tile.y != 0
        assert tile.x != 4
        assert tile.y != 4
