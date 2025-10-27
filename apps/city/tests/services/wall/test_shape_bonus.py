import pytest

from apps.city.models import Tile
from apps.city.services.wall.shape_bonus import WallShapeBonusService
from apps.city.tests.factories import BuildingFactory, TerrainFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_shape_bonus_service_no_walls():
    """Test that service returns 0 when there are no walls."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create map without walls
    tiles = [TileFactory.build(savegame=savegame, terrain=terrain, building=None, x=i % 5, y=i // 5) for i in range(25)]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    assert result == 0


@pytest.mark.django_db
def test_shape_bonus_service_single_wall():
    """Test that service returns 0 for a single wall (no neighbors)."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    wall = BuildingFactory(building_type=wall_type)

    # Create map with single wall in center
    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall if (x == 2 and y == 2) else None,
            x=x,
            y=y,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # Single wall has 0 neighbors, so no bonus
    assert result == 0


@pytest.mark.django_db
def test_shape_bonus_service_straight_wall():
    """Test that service awards bonus for straight wall (each wall has 2 neighbors)."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create straight horizontal wall
    # . . . . .
    # . W W W .
    # . . . . .

    wall_positions = [(1, 1), (2, 1), (3, 1)]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(3)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # Middle wall (2,1) has 2 neighbors
    # End walls (1,1) and (3,1) have 1 neighbor each
    # Expected: 1 smooth wall * 5 points = 5
    assert result == 5


@pytest.mark.django_db
def test_shape_bonus_service_l_shape():
    """Test that service awards bonus for L-shaped wall configuration."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create L-shaped wall
    # W . .
    # W . .
    # W W W

    wall_positions = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(3)
        for x in range(3)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # (0,1) has 2 neighbors: up and down
    # (1,2) has 2 neighbors: left and right
    # Corner (0,2) has 2 neighbors: up and right
    # (0,0) has 1 neighbor, (2,2) has 1 neighbor
    # Expected: 3 smooth walls * 5 points = 15
    assert result == 15


@pytest.mark.django_db
def test_shape_bonus_service_enclosed_square():
    """Test that service awards bonus for enclosed square wall."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create square wall perimeter (5x5 outer edge)
    # W W W W W
    # W . . . W
    # W . . . W
    # W . . . W
    # W W W W W

    wall_positions = [(x, y) for y in range(5) for x in range(5) if x == 0 or x == 4 or y == 0 or y == 4]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # All walls except corners have exactly 2 neighbors
    # Total walls = 16 (perimeter of 5x5 square)
    # Corners (4 walls) have 2 neighbors each
    # Edge walls (12 walls) have 2 neighbors each
    # All 16 walls should be smooth
    # Expected: 16 smooth walls * 5 points = 80
    assert result == 80


@pytest.mark.django_db
def test_shape_bonus_service_t_junction():
    """Test that T-junction walls get no bonus (3 neighbors)."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create T-junction
    # . W .
    # W W W
    # . W .

    wall_positions = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(3)
        for x in range(3)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # Center wall (1,1) has 4 neighbors (up, down, left, right) - no bonus
    # All other walls have 1-2 neighbors
    # (1,0) has 1 neighbor, (0,1) has 1 neighbor, (2,1) has 1 neighbor, (1,2) has 1 neighbor
    # Expected: 0 smooth walls * 5 points = 0
    assert result == 0


@pytest.mark.django_db
def test_shape_bonus_service_cross_shape():
    """Test that cross-shaped wall configuration gets no bonus for center."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create cross shape
    # . . W . .
    # . . W . .
    # W W W W W
    # . . W . .
    # . . W . .

    wall_positions = [(2, 0), (2, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (2, 3), (2, 4)]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # Center wall (2,2) has 4 neighbors - no bonus
    # Walls at (2,1), (1,2), (3,2), (2,3) have 2 neighbors each - bonus
    # End walls have 1 neighbor each - no bonus
    # Expected: 4 smooth walls * 5 points = 20
    assert result == 20


@pytest.mark.django_db
def test_shape_bonus_service_map_edge():
    """Test that walls at map edge are correctly evaluated."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create wall at map edge (left edge)
    # W . .
    # W . .
    # W . .

    wall_positions = [(0, 0), (0, 1), (0, 2)]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(3)
        for x in range(3)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # Middle wall (0,1) has 2 neighbors (up and down)
    # End walls (0,0) and (0,2) have 1 neighbor each
    # Expected: 1 smooth wall * 5 points = 5
    assert result == 5


@pytest.mark.django_db
def test_shape_bonus_service_disconnected_walls():
    """Test that disconnected wall groups are evaluated independently."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create two disconnected wall segments
    # W W . W W
    # . . . . .

    wall_positions = [(0, 0), (1, 0), (3, 0), (4, 0)]
    wall_buildings = {pos: BuildingFactory(building_type=wall_type) for pos in wall_positions}

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y)),
            x=x,
            y=y,
        )
        for y in range(2)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    service = WallShapeBonusService(savegame=savegame)
    result = service.process()

    # Left segment: (0,0) and (1,0) - neither has 2 neighbors
    # (0,0) has 1 neighbor, (1,0) has 1 neighbor
    # Right segment: (3,0) and (4,0) - neither has 2 neighbors
    # (3,0) has 1 neighbor, (4,0) has 1 neighbor
    # Expected: 0 smooth walls * 5 points = 0
    assert result == 0
