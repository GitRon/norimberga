import pytest

from apps.city.services.wall.enclosure import WallEnclosureService
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    SavegameFactory,
    TerrainFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
    WallBuildingTypeFactory,
    WaterTerrainFactory,
)


@pytest.mark.django_db
def test_wall_enclosure_service_no_city_buildings():
    """Test that service returns False when there are no city buildings."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create map without city buildings
    for x in range(5):
        for y in range(5):
            TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_city_not_enclosed():
    """Test that service returns False when city buildings are not enclosed by walls."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create city building type
    city_building_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])
    city_building = BuildingFactory(building_type=city_building_type)

    # Create map with city building in center (not enclosed)
    for x in range(5):
        for y in range(5):
            if x == 2 and y == 2:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city_building)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_city_enclosed_by_walls():
    """Test that service returns True when city buildings are enclosed by walls."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create map: wall around the edge, city building in center
    # Map layout (5x5):
    # W W W W W
    # W C C C W
    # W C C C W
    # W C C C W
    # W W W W W

    for x in range(5):
        for y in range(5):
            # Walls on the edges
            if x == 0 or x == 4 or y == 0 or y == 4:
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            # City building in center
            elif x == 2 and y == 2:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_gap_in_wall():
    """Test that service returns False when there is a gap in the wall."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create map with gap in wall at position (4, 2)
    # W W W W W
    # W C C C W
    # W C C C .  <- gap here
    # W C C C W
    # W W W W W

    for x in range(5):
        for y in range(5):
            # Walls on the edges, except gap at (4, 2)
            if (x == 0 or x == 4 or y == 0 or y == 4) and not (x == 4 and y == 2):
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            # City building in center
            elif x == 2 and y == 2:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_multiple_city_buildings():
    """Test that service works with multiple city buildings inside walls."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create map with multiple city buildings
    for x in range(5):
        for y in range(5):
            # Walls on the edges
            if x == 0 or x == 4 or y == 0 or y == 4:
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            # City buildings scattered inside
            elif (x == 1 and y == 1) or (x == 2 and y == 2) or (x == 3 and y == 3):
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_city_building_outside_wall():
    """Test that service returns False when a city building is outside the wall."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create map: small wall in center, city building outside
    # . . C . .
    # . W W W .
    # C W C W C
    # . W W W .
    # . . C . .

    for x in range(5):
        for y in range(5):
            # Small wall in center
            if ((x == 1 or x == 3) and (1 <= y <= 3)) or ((y == 1 or y == 3) and (1 <= x <= 3)):
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            # City building inside wall
            elif (x == 2 and y == 2) or (x == 2 and y == 0) or (x == 0 and y == 2):
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_starts_from_unique_building():
    """Test that service prefers starting from a unique building."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    unique_type = UniqueBuildingTypeFactory(allowed_terrains=[terrain])

    # Create map with unique building in center, surrounded by walls
    for x in range(5):
        for y in range(5):
            if x == 0 or x == 4 or y == 0 or y == 4:
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            elif x == 2 and y == 2:
                unique = BuildingFactory(building_type=unique_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=unique)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)

    # Get city building tiles
    city_tiles = service._get_city_building_tiles()
    assert len(city_tiles) == 1

    # Get starting tile - should be the unique building
    start_tile = service._get_starting_tile(city_tiles=city_tiles)
    assert start_tile.building.building_type.is_unique is True

    # Overall result should be True (enclosed)
    result = service.process()
    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_3x3_map():
    """Test enclosure detection on a smaller 3x3 map."""
    savegame = SavegameFactory(map_size=3)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create 3x3 map fully enclosed
    # W W W
    # W C W
    # W W W

    for x in range(3):
        for y in range(3):
            if x == 0 or x == 2 or y == 0 or y == 2:
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            else:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_water_only_does_not_enclose():
    """Test that a city cannot be enclosed by water alone without walls."""
    savegame = SavegameFactory(map_size=5)
    land_terrain = TerrainFactory(is_water=False)
    water_terrain = WaterTerrainFactory()

    # Create building type
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[land_terrain])

    # Create map: water completely surrounds city
    # ~ ~ ~ ~ ~
    # ~ C C C ~
    # ~ C C C ~
    # ~ C C C ~
    # ~ ~ ~ ~ ~

    for x in range(5):
        for y in range(5):
            # Water on edges
            if x == 0 or x == 4 or y == 0 or y == 4:
                TileFactory(savegame=savegame, x=x, y=y, terrain=water_terrain, building=None)
            # City buildings in center
            elif x == 2 and y == 2:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    # Water alone doesn't count as enclosure - only wall buildings do
    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_gap_in_water():
    """Test that a gap in water terrain is detected (city not enclosed)."""
    savegame = SavegameFactory(map_size=5)
    land_terrain = TerrainFactory(is_water=False)
    water_terrain = WaterTerrainFactory()

    # Create building type
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[land_terrain])

    # Create map: water with gap on right edge at (4, 2)
    # ~ ~ ~ ~ ~
    # ~ C C C ~
    # ~ C C C .  <- gap here (land instead of water)
    # ~ C C C ~
    # ~ ~ ~ ~ ~

    for x in range(5):
        for y in range(5):
            # Water on edges, except gap at (4, 2)
            if (x == 0 or x == 4 or y == 0 or y == 4) and not (x == 4 and y == 2):
                TileFactory(savegame=savegame, x=x, y=y, terrain=water_terrain, building=None)
            # City building in center
            elif x == 2 and y == 2:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_mixed_water_and_walls():
    """Test that water does not work with walls to enclose a city - only walls count."""
    savegame = SavegameFactory(map_size=5)
    land_terrain = TerrainFactory(is_water=False)
    water_terrain = WaterTerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[land_terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[land_terrain])

    # Create map: mix of water and walls
    # ~ ~ W W W  (~ = water, W = wall, C = city, . = land)
    # ~ . . . W
    # W . C . W
    # ~ . . . W
    # ~ ~ W W W

    for x in range(5):
        for y in range(5):
            # Top row: water then walls
            if y == 0 or y == 4:
                if x < 2:
                    TileFactory(savegame=savegame, x=x, y=y, terrain=water_terrain, building=None)
                else:
                    wall = BuildingFactory(building_type=wall_type)
                    TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=wall)
            # Left edge: water then wall
            elif x == 0:
                if y < 2:
                    TileFactory(savegame=savegame, x=x, y=y, terrain=water_terrain, building=None)
                else:
                    wall = BuildingFactory(building_type=wall_type)
                    TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=wall)
            # Right edge: all walls
            elif x == 4:
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=wall)
            # Center: city building at (2, 2)
            elif x == 2 and y == 2:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=land_terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    # Water doesn't count as wall, so flood fill can reach water tiles at edge
    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_with_missing_tiles():
    """Test that service handles missing tiles gracefully (Tile.DoesNotExist exception)."""
    savegame = SavegameFactory(map_size=5)
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create incomplete map with city building in center, walls around it, but some tiles missing
    # W W W W W
    # W C C C W
    # W C C C W  <- tile at (3, 2) is missing from database
    # W C C C W
    # W W W W W

    for x in range(5):
        for y in range(5):
            # Skip creating tile at (3, 2) to trigger Tile.DoesNotExist
            if x == 3 and y == 2:
                continue

            # Walls on the edges
            if x == 0 or x == 4 or y == 0 or y == 4:
                wall = BuildingFactory(building_type=wall_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=wall)
            # City building in center
            elif x == 2 and y == 2:
                city = BuildingFactory(building_type=city_type)
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=city)
            else:
                TileFactory(savegame=savegame, x=x, y=y, terrain=terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    # The missing tile should be skipped, and enclosure should still be detected
    assert result is True
