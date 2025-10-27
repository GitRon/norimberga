import pytest

from apps.city.models import Tile
from apps.city.services.wall.spike_malus import WallSpikeMalusService
from apps.city.tests.factories import BuildingFactory, TerrainFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_spike_malus_service_no_walls():
    """Test that service returns 0 when there are no walls."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create map without walls
    tiles = [TileFactory.build(savegame=savegame, terrain=terrain, building=None, x=i % 5, y=i // 5) for i in range(25)]
    Tile.objects.bulk_create(tiles)

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    assert result == 0


@pytest.mark.django_db
def test_spike_malus_service_single_wall():
    """Test that service applies malus for a single wall (0 neighbors)."""
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # Single wall has 0 neighbors, so 1 spike * -10 malus = -10
    assert result == -10


@pytest.mark.django_db
def test_spike_malus_service_two_adjacent_walls():
    """Test that service applies malus for walls with only 1 neighbor."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create two adjacent walls
    # W W . . .
    # . . . . .

    wall_positions = [(0, 0), (1, 0)]
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # Both walls have 1 neighbor each, so 2 spikes * -10 malus = -20
    assert result == -20


@pytest.mark.django_db
def test_spike_malus_service_straight_wall():
    """Test that service gives no malus for straight wall (middle wall has 2 neighbors)."""
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # Middle wall (2,1) has 2 neighbors - no malus
    # End walls (1,1) and (3,1) have 1 neighbor each - malus
    # Expected: 2 spikes * -10 malus = -20
    assert result == -20


@pytest.mark.django_db
def test_spike_malus_service_enclosed_square():
    """Test that service gives no malus for enclosed square wall (all have 2 neighbors)."""
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # All walls in square have exactly 2 neighbors, so no spikes
    # Expected: 0 spikes * -10 malus = 0
    assert result == 0


@pytest.mark.django_db
def test_spike_malus_service_square_with_gap():
    """Test that service applies malus for walls near a gap."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create square with gap (missing corner)
    # W W W W .
    # W . . . W
    # W . . . W
    # W . . . W
    # W W W W W

    wall_positions = [
        (x, y) for y in range(5) for x in range(5) if (x == 0 or x == 4 or y == 0 or y == 4) and not (x == 4 and y == 0)
    ]
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # Two walls adjacent to the gap will have only 1 neighbor each
    # (3,0) has 1 neighbor (left), (4,1) has 1 neighbor (down)
    # Expected: 2 spikes * -10 malus = -20
    assert result == -20


@pytest.mark.django_db
def test_spike_malus_service_t_junction():
    """Test that T-junction walls are not penalized (center has 4 neighbors, arms have varying neighbors)."""
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # Center wall (1,1) has 4 neighbors - no malus (>1 neighbor)
    # All other walls have 1 neighbor each
    # (1,0), (0,1), (2,1), (1,2) each have 1 neighbor
    # Expected: 4 spikes * -10 malus = -40
    assert result == -40


@pytest.mark.django_db
def test_spike_malus_service_disconnected_walls():
    """Test that disconnected wall segments all get malus."""
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # All 4 walls have 1 neighbor each, so all are spikes
    # Expected: 4 spikes * -10 malus = -40
    assert result == -40


@pytest.mark.django_db
def test_spike_malus_service_map_edge():
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # Middle wall (0,1) has 2 neighbors (up and down) - no malus
    # End walls (0,0) and (0,2) have 1 neighbor each - malus
    # Expected: 2 spikes * -10 malus = -20
    assert result == -20


@pytest.mark.django_db
def test_spike_malus_service_l_shape():
    """Test that L-shaped wall configuration applies malus appropriately."""
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

    service = WallSpikeMalusService(savegame=savegame)
    result = service.process()

    # (0,1) has 2 neighbors: up and down - no malus
    # (1,2) has 2 neighbors: left and right - no malus
    # Corner (0,2) has 2 neighbors: up and right - no malus
    # (0,0) has 1 neighbor - malus
    # (2,2) has 1 neighbor - malus
    # Expected: 2 spikes * -10 malus = -20
    assert result == -20
