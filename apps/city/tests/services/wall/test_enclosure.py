import pytest

from apps.city.models import Tile
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
    WallBuildingTypeFactory,
    WaterTerrainFactory,
)
from apps.savegame.tests.factories import SavegameFactory


def create_tiles_batch(savegame, size, terrain, building=None):
    """Helper to batch create tiles for a square map."""
    # Create tiles manually to avoid factory.Sequence global counter issues
    # Using list comprehension with bulk_create for performance
    tiles = [
        TileFactory.build(savegame=savegame, terrain=terrain, building=building, x=i % size, y=i // size)
        for i in range(size * size)
    ]

    return TileFactory._meta.model.objects.bulk_create(tiles)


@pytest.mark.django_db
def test_wall_enclosure_service_no_city_buildings():
    """Test that service returns False when there are no city buildings."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create map without city buildings
    create_tiles_batch(savegame, 5, terrain, building=None)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_city_not_enclosed():
    """Test that service returns False when city buildings are not enclosed by walls."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create city building type
    city_building_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])
    city_building = BuildingFactory(building_type=city_building_type)

    # Create map with city building in center (not enclosed)
    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=city_building if (x == 2 and y == 2) else None,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_city_enclosed_by_walls():
    """Test that service returns True when city buildings are enclosed by walls."""
    savegame = SavegameFactory()
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

    # Pre-create buildings for positions that need them
    wall_buildings = {
        (x, y): BuildingFactory(building_type=wall_type)
        for y in range(5)
        for x in range(5)
        if x == 0 or x == 4 or y == 0 or y == 4
    }
    city_building = BuildingFactory(building_type=city_type)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=wall_buildings.get((x, y))
            if (x == 0 or x == 4 or y == 0 or y == 4)
            else (city_building if (x == 2 and y == 2) else None),
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_gap_in_wall():
    """Test that service returns False when there is a gap in the wall."""
    map_size = 10
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create a smaller enclosed area with walls, but create enough tiles for the service to work
    # We'll create tiles in a 10x10 map, with a gap in the wall

    # Create all tiles for the map using bulk_create for performance
    tiles = [
        TileFactory.build(savegame=savegame, x=i % map_size, y=i // map_size, terrain=terrain, building=None)
        for i in range(map_size * map_size)
    ]
    Tile.objects.bulk_create(tiles)

    # Now add walls in a ring around position (3, 3) with a gap
    # W W W W W
    # W C C C W
    # W C C C .  <- gap at (7, 5) allows escape to edge
    # W C C C W
    # W W W W W

    for dx in range(5):
        for dy in range(5):
            x, y = 3 + dx, 3 + dy
            # Walls on the edges, except gap at (7, 5)
            if (dx == 0 or dx == 4 or dy == 0 or dy == 4) and not (dx == 4 and dy == 2):
                wall = BuildingFactory(building_type=wall_type)
                tile = Tile.objects.get(savegame=savegame, x=x, y=y)
                tile.building = wall
                tile.save()
            # City building in center
            elif dx == 2 and dy == 2:
                city = BuildingFactory(building_type=city_type)
                tile = Tile.objects.get(savegame=savegame, x=x, y=y)
                tile.building = city
                tile.save()

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_multiple_city_buildings():
    """Test that service works with multiple city buildings inside walls."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create map with multiple city buildings
    # Pre-create buildings for positions that need them
    wall_buildings = {
        (x, y): BuildingFactory(building_type=wall_type)
        for y in range(5)
        for x in range(5)
        if x == 0 or x == 4 or y == 0 or y == 4
    }
    city_buildings = {(x, y): BuildingFactory(building_type=city_type) for x, y in [(1, 1), (2, 2), (3, 3)]}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=wall_buildings.get((x, y)) or city_buildings.get((x, y)),
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_city_building_outside_wall():
    """Test that service returns False when a city building is outside the wall."""
    savegame = SavegameFactory()
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

    # Pre-create buildings for positions that need them
    wall_buildings = {
        (x, y): BuildingFactory(building_type=wall_type)
        for y in range(5)
        for x in range(5)
        if ((x == 1 or x == 3) and (1 <= y <= 3)) or ((y == 1 or y == 3) and (1 <= x <= 3))
    }
    city_buildings = {(x, y): BuildingFactory(building_type=city_type) for x, y in [(2, 2), (2, 0), (0, 2)]}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=wall_buildings.get((x, y)) or city_buildings.get((x, y)),
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_starts_from_unique_building():
    """Test that service prefers starting from a unique building."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    unique_type = UniqueBuildingTypeFactory(allowed_terrains=[terrain])

    # Create map with unique building in center, surrounded by walls
    # Pre-create buildings for positions that need them
    wall_buildings = {
        (x, y): BuildingFactory(building_type=wall_type)
        for y in range(5)
        for x in range(5)
        if x == 0 or x == 4 or y == 0 or y == 4
    }
    unique_building = BuildingFactory(building_type=unique_type)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=wall_buildings.get((x, y))
            if (x == 0 or x == 4 or y == 0 or y == 4)
            else (unique_building if (x == 2 and y == 2) else None),
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

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
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create 3x3 map fully enclosed
    # W W W
    # W C W
    # W W W

    # Pre-create buildings for positions that need them
    wall_buildings = {
        (x, y): BuildingFactory(building_type=wall_type)
        for y in range(3)
        for x in range(3)
        if x == 0 or x == 2 or y == 0 or y == 2
    }
    city_building = BuildingFactory(building_type=city_type)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=wall_buildings.get((x, y)) if (x == 0 or x == 2 or y == 0 or y == 2) else city_building,
        )
        for y in range(3)
        for x in range(3)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is True


@pytest.mark.django_db
def test_wall_enclosure_service_water_only_does_not_enclose():
    """Test that a city cannot be enclosed by water alone without walls."""
    savegame = SavegameFactory()
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

    city_building = BuildingFactory(building_type=city_type)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=water_terrain if (x == 0 or x == 4 or y == 0 or y == 4) else land_terrain,
            building=city_building if (x == 2 and y == 2) else None,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    # Water alone doesn't count as enclosure - only wall buildings do
    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_gap_in_water():
    """Test that a gap in water terrain is detected (city not enclosed)."""
    savegame = SavegameFactory()
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

    city_building = BuildingFactory(building_type=city_type)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=water_terrain
            if ((x == 0 or x == 4 or y == 0 or y == 4) and not (x == 4 and y == 2))
            else land_terrain,
            building=city_building if (x == 2 and y == 2) else None,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_mixed_water_and_walls():
    """Test that water does not work with walls to enclose a city - only walls count."""
    savegame = SavegameFactory()
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

    # Pre-create buildings for positions that need them
    wall_positions = [
        (x, y) for y in range(5) for x in range(5) if ((y == 0 or y == 4) and x >= 2) or (x == 0 and y >= 2) or x == 4
    ]

    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}
    city_building = BuildingFactory(building_type=city_type)

    def get_tile_data(x, y):
        # Top/bottom rows: water if x < 2, else wall
        if y == 0 or y == 4:
            if x < 2:
                return water_terrain, None
            else:
                return land_terrain, wall_buildings.get((x, y))
        # Left edge: water if y < 2, else wall
        elif x == 0:
            if y < 2:
                return water_terrain, None
            else:
                return land_terrain, wall_buildings.get((x, y))
        # Right edge: all walls
        elif x == 4:
            return land_terrain, wall_buildings.get((x, y))
        # Center: city building at (2, 2)
        elif x == 2 and y == 2:
            return land_terrain, city_building
        else:
            return land_terrain, None

    tiles = [
        TileFactory.build(savegame=savegame, x=x, y=y, terrain=terrain, building=building)
        for y in range(5)
        for x in range(5)
        for terrain, building in [get_tile_data(x, y)]
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    # Water doesn't count as wall, so flood fill can reach water tiles at edge
    assert result is False


@pytest.mark.django_db
def test_wall_enclosure_service_with_missing_tiles():
    """Test that service handles missing tiles gracefully (Tile.DoesNotExist exception)."""
    savegame = SavegameFactory()
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

    # Pre-create buildings for positions that need them
    wall_buildings = {
        (x, y): BuildingFactory(building_type=wall_type)
        for y in range(5)
        for x in range(5)
        if x == 0 or x == 4 or y == 0 or y == 4
    }
    city_building = BuildingFactory(building_type=city_type)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            x=x,
            y=y,
            terrain=terrain,
            building=wall_buildings.get((x, y))
            if (x == 0 or x == 4 or y == 0 or y == 4)
            else (city_building if (x == 2 and y == 2) else None),
        )
        for y in range(5)
        for x in range(5)
        if not (x == 3 and y == 2)  # Skip tile at (3, 2)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallEnclosureService(savegame=savegame)
    result = service.process()

    # The missing tile should be skipped, and enclosure should still be detected
    assert result is True
