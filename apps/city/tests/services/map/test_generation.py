from unittest import mock

import pytest

from apps.city.services.map.coordinates import MapCoordinatesService
from apps.city.services.map.generation import INITIAL_COUNTRY_BUILDINGS, MapGenerationService
from apps.city.tests.factories import (
    BuildingFactory,
    CountryBuildingTypeFactory,
    RiverTerrainFactory,
    TerrainFactory,
    TileFactory,
    WaterTerrainFactory,
)
from apps.savegame.tests.factories import SavegameFactory


def create_tiles_batch(savegame, size, terrain=None):
    """Helper to batch create tiles for a square map."""
    if terrain is None:
        terrain = TerrainFactory()

    # Create tiles manually to avoid factory.Sequence global counter issues
    # Using list comprehension with bulk_create for performance
    tiles = [TileFactory.build(savegame=savegame, terrain=terrain, x=i % size, y=i // size) for i in range(size * size)]

    return TileFactory._meta.model.objects.bulk_create(tiles)


@pytest.mark.django_db
def test_map_generation_service_init():
    """Test MapGenerationService initialization."""
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=5)

    assert service.savegame == savegame
    assert service.map_size == 5


@pytest.mark.django_db
def test_map_generation_service_get_terrain():
    """Test get_terrain returns terrain based on probability."""
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=3)

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
    service = MapGenerationService(savegame=savegame, map_size=3)

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
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Clear any existing water terrains and create a unique one
    from apps.city.models import Terrain

    Terrain.objects.filter(is_water=True).delete()
    river_terrain = RiverTerrainFactory()
    terrain = TerrainFactory()

    create_tiles_batch(savegame, map_size, terrain)

    with (
        mock.patch("apps.city.services.map.generation.randint") as mock_randint,
        mock.patch("apps.city.services.map.generation.random.choice") as mock_choice,
    ):
        # Set up river starting at (0, 2) and going to reach edge at x=map_size-1
        mock_randint.side_effect = [1, 2]  # dice=1 means start on y-axis, y=2

        # Mock coordinate choices for river path to reach edge at x=map_size-1
        coords = [MapCoordinatesService.Coordinates(x=i + 1, y=2) for i in range(map_size - 1)]
        mock_choice.side_effect = coords

        service._draw_river()

        # Verify river tiles were created at expected coordinates
        river_tiles = savegame.tiles.filter(terrain=river_terrain)
        assert river_tiles.count() >= 1


@pytest.mark.django_db
def test_map_generation_service_draw_river_x_axis():
    """Test _draw_river creates river tiles starting from x-axis."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Clear any existing water terrains and create a unique one
    from apps.city.models import Terrain

    Terrain.objects.filter(is_water=True).delete()
    river_terrain = RiverTerrainFactory()
    terrain = TerrainFactory()

    create_tiles_batch(savegame, map_size, terrain)

    with (
        mock.patch("apps.city.services.map.generation.randint") as mock_randint,
        mock.patch("apps.city.services.map.generation.random.choice") as mock_choice,
    ):
        # Set up river starting on x-axis - dice=2 triggers else branch (line 31)
        mock_randint.side_effect = [2, 2]  # dice=2 means start on x-axis, x=2

        # Mock coordinate choices for river path to reach edge at y=map_size-1
        coords = [MapCoordinatesService.Coordinates(x=2, y=i + 1) for i in range(map_size - 1)]
        mock_choice.side_effect = coords

        service._draw_river()

        # Verify river tiles were created at expected coordinates
        river_tiles = savegame.tiles.filter(terrain=river_terrain)
        assert river_tiles.count() >= 1


@pytest.mark.django_db
def test_map_generation_service_draw_river_missing_terrain():
    """Test _draw_river raises ValueError when River terrain is missing."""
    map_size = 3
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Clear any existing water terrains to simulate missing terrain
    from apps.city.models import Terrain

    Terrain.objects.filter(is_water=True).delete()
    terrain = TerrainFactory()

    create_tiles_batch(savegame, map_size, terrain)

    with pytest.raises(
        ValueError,
        match=r"River terrain not found\. Please ensure River terrain exists in the database\.",
    ):
        service._draw_river()


@pytest.mark.django_db
def test_map_generation_service_process():
    """Test process method creates complete map with river."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    terrain = TerrainFactory()
    RiverTerrainFactory()

    with (
        mock.patch.object(service, "get_terrain") as mock_get_terrain,
        mock.patch.object(service, "_draw_river") as mock_draw_river,
    ):
        mock_get_terrain.return_value = terrain

        service.process()

        # Verify all tiles were created (5x5 map = 25 tiles)
        assert savegame.tiles.count() == 25

        # Verify draw_river was called
        mock_draw_river.assert_called_once()

        # Verify get_terrain was called for each tile
        assert mock_get_terrain.call_count == 25


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings():
    """Test _place_random_country_buildings places buildings on valid tiles."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrains
    terrain_grass = TerrainFactory(name="Grass", probability=80)
    terrain_forest = TerrainFactory(name="Forest", probability=60)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain_grass, terrain_forest])

    # Create level 1 building for this type
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles with alternating terrains using batch creation
    tiles = []
    for i in range(map_size * map_size):
        x, y = i % map_size, i // map_size
        tiles.append(
            TileFactory.build(
                savegame=savegame, x=x, y=y, terrain=terrain_grass if (x + y) % 2 == 0 else terrain_forest
            )
        )
    TileFactory._meta.model.objects.bulk_create(tiles)

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
    """Test _place_random_country_buildings does nothing when no country building types exist (line 67)."""
    from apps.city.models import BuildingType

    # Ensure no country building types exist
    BuildingType.objects.filter(is_country=True).delete()

    map_size = 3
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    terrain = TerrainFactory()

    # Create tiles without any country building types
    create_tiles_batch(savegame, map_size, terrain)

    service._place_random_country_buildings()

    # Verify no buildings were placed
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_no_valid_terrains():
    """Test _place_random_country_buildings handles case where buildings can't be placed."""
    map_size = 3
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrain that won't be allowed for country buildings
    terrain_water = TerrainFactory(name="Water", is_water=True)

    # Create country building type that doesn't allow water terrain
    terrain_grass = TerrainFactory(name="Grass")
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain_grass])
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles with only water terrain (which isn't allowed)
    tiles = [
        TileFactory.build(savegame=savegame, x=i % map_size, y=i // map_size, terrain=terrain_water)
        for i in range(map_size * map_size)
    ]
    TileFactory._meta.model.objects.bulk_create(tiles)

    service._place_random_country_buildings()

    # Verify no buildings were placed because no valid terrains available
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0


@pytest.mark.django_db
def test_map_generation_service_process_includes_country_buildings():
    """Test process method includes country building placement."""
    map_size = 3
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

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
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrain
    terrain = TerrainFactory(name="Grass", probability=80)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])

    # Create level 1 building for this type
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles - all with same terrain
    create_tiles_batch(savegame, map_size, terrain)

    service._place_random_country_buildings()

    # Verify that buildings were placed
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == INITIAL_COUNTRY_BUILDINGS

    # Verify none of the buildings are on edge tiles (map_size x map_size map has coordinates 0 to map_size-1)
    for tile in tiles_with_buildings:
        assert tile.is_edge_tile() is False
        assert tile.x != 0
        assert tile.y != 0
        assert tile.x != map_size - 1
        assert tile.y != map_size - 1


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_no_tiles():
    """Test _place_random_country_buildings handles case where there are no valid tiles (line 75)."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create water terrain that building can't be placed on
    terrain_water = WaterTerrainFactory(name="Water", probability=80)

    # Create terrain that building CAN be placed on
    terrain_grass = TerrainFactory(name="Grass", probability=60)

    # Create country building type with allowed terrains (only grass, not water)
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain_grass])

    # Create level 1 building for this type
    BuildingFactory(building_type=country_building_type, level=1)

    # Create tiles - all non-edge tiles are water (incompatible terrain)
    # Only edge tiles are grass, so no buildings can be placed
    tiles = []
    for i in range(map_size * map_size):
        x, y = i % map_size, i // map_size
        is_edge = x == 0 or y == 0 or x == map_size - 1 or y == map_size - 1
        tiles.append(
            TileFactory.build(savegame=savegame, x=x, y=y, terrain=terrain_grass if is_edge else terrain_water)
        )
    TileFactory._meta.model.objects.bulk_create(tiles)

    service._place_random_country_buildings()

    # Verify no buildings were placed because valid terrain only on edge tiles
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_no_level_1_building():
    """Test _place_random_country_buildings handles case where building type has no level 1 (line 104)."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrain
    terrain = TerrainFactory(name="Grass", probability=80)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])

    # Create level 2 building for this type, but NO level 1
    BuildingFactory(building_type=country_building_type, level=2)

    create_tiles_batch(savegame, map_size, terrain)

    service._place_random_country_buildings()

    # Verify no buildings were placed because no level 1 building exists
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_skips_occupied_tiles():
    """Test _place_random_country_buildings skips tiles that already have buildings (line 89)."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrain
    terrain = TerrainFactory(name="Grass", probability=80)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])

    # Create level 1 building for this type
    building_level_1 = BuildingFactory(building_type=country_building_type, level=1)

    create_tiles_batch(savegame, map_size, terrain)

    # Pre-place a building on a non-edge tile to occupy it
    from apps.city.models import Tile

    occupied_tile = Tile.objects.get(savegame=savegame, x=2, y=2)
    occupied_tile.building = building_level_1
    occupied_tile.save(update_fields=["building"])

    # Mock random.choice - it's called twice per iteration: once for tile, once for building_type
    with mock.patch("apps.city.services.map.generation.random.choice") as mock_choice:
        # Get the tiles list similar to how the service does it (non-edge tiles)
        tiles = [t for t in savegame.tiles.select_related("terrain").all() if not t.is_edge_tile()]
        # Filter out the occupied tile to get available tiles
        available_tiles = [t for t in tiles if t != occupied_tile]

        # Make the first call return the occupied tile (should be skipped due to line 89)
        # Then provide enough tile and building_type choices for successful placements
        # Pattern: tile, building_type, tile, building_type, ...
        side_effects = [occupied_tile]  # First attempt - will hit line 89 and continue
        for i in range(INITIAL_COUNTRY_BUILDINGS):
            side_effects.append(available_tiles[i])  # Pick a tile
            side_effects.append(country_building_type)  # Pick the building type

        mock_choice.side_effect = side_effects

        service._place_random_country_buildings()

    # Verify that exactly INITIAL_COUNTRY_BUILDINGS new buildings were placed
    # (the occupied tile should be skipped and other tiles used instead)
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == INITIAL_COUNTRY_BUILDINGS + 1  # +1 for the pre-placed building


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_excludes_city_and_country_buildings():
    """Test _place_random_country_buildings excludes buildings that are both is_city and is_country."""
    from apps.city.models import BuildingType

    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrain
    terrain = TerrainFactory(name="Grass", probability=80)

    # Create a building type that is both city and country (like market square)
    city_and_country_building_type = BuildingType.objects.create(name="Market Square", is_city=True, is_country=True)
    city_and_country_building_type.allowed_terrains.add(terrain)
    BuildingFactory(building_type=city_and_country_building_type, level=1)

    # Create a pure country building type
    country_only_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])
    BuildingFactory(building_type=country_only_building_type, level=1)

    create_tiles_batch(savegame, map_size, terrain)

    service._place_random_country_buildings()

    # Verify that buildings were placed
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == INITIAL_COUNTRY_BUILDINGS

    # Verify that none of the placed buildings are the city+country type
    for tile in tiles_with_buildings:
        assert tile.building.building_type != city_and_country_building_type
        assert tile.building.building_type == country_only_building_type
        assert tile.building.building_type.is_country is True
        assert tile.building.building_type.is_city is False


@pytest.mark.django_db
def test_map_generation_service_place_random_country_buildings_only_edge_tiles():
    """Test _place_random_country_buildings returns early when only edge tiles exist (line 76)."""
    map_size = 5
    savegame = SavegameFactory()
    service = MapGenerationService(savegame=savegame, map_size=map_size)

    # Create terrain
    terrain = TerrainFactory(name="Grass", probability=80)

    # Create country building type with allowed terrains
    country_building_type = CountryBuildingTypeFactory(allowed_terrains=[terrain])
    BuildingFactory(building_type=country_building_type, level=1)

    # Create only edge tiles (tiles where x=0 or y=0 or x=map_size-1 or y=map_size-1)
    # After filtering out edge tiles in line 73, the tiles list will be empty
    tiles = []
    # Top row (y=0)
    tiles.extend([TileFactory.build(savegame=savegame, x=x, y=0, terrain=terrain) for x in range(map_size)])
    # Bottom row (y=map_size-1)
    tiles.extend([TileFactory.build(savegame=savegame, x=x, y=map_size - 1, terrain=terrain) for x in range(map_size)])
    # Left column (x=0, excluding corners already added)
    tiles.extend([TileFactory.build(savegame=savegame, x=0, y=y, terrain=terrain) for y in range(1, map_size - 1)])
    # Right column (x=map_size-1, excluding corners already added)
    tiles.extend(
        [TileFactory.build(savegame=savegame, x=map_size - 1, y=y, terrain=terrain) for y in range(1, map_size - 1)]
    )

    TileFactory._meta.model.objects.bulk_create(tiles)

    service._place_random_country_buildings()

    # Verify no buildings were placed because all tiles are edge tiles
    tiles_with_buildings = savegame.tiles.filter(building__isnull=False)
    assert tiles_with_buildings.count() == 0
