from unittest import mock

import pytest

from apps.city.models import Tile
from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
    WallBuildingTypeFactory,
)
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_defense_calculation_service_walls_not_enclosed():
    """Test that service returns 0 when walls are not enclosed."""
    savegame = SavegameFactory.create()

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = False

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 50

    mock_spike_malus_service = mock.Mock()
    mock_spike_malus_service.process.return_value = -10

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
        spike_malus_service=mock_spike_malus_service,
    )
    result = service.process()

    # When not enclosed, defense should be 0
    assert result == 0
    # All services should be called to calculate breakdown
    mock_enclosure_service.process.assert_called_once()
    mock_shape_bonus_service.process.assert_called_once()
    mock_spike_malus_service.process.assert_called_once()


@pytest.mark.django_db
def test_defense_calculation_service_walls_enclosed_no_buildings():
    """Test that service returns only shape bonus when enclosed but no buildings have defense."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create tiles without buildings
    tiles = [TileFactory.build(savegame=savegame, terrain=terrain, building=None, x=i % 5, y=i // 5) for i in range(25)]
    Tile.objects.bulk_create(tiles)

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = True

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 50

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
    )
    result = service.process()

    # Expected: 0 base defense + 50 shape bonus = 50
    assert result == 50
    mock_enclosure_service.process.assert_called_once()
    mock_shape_bonus_service.process.assert_called_once()


@pytest.mark.django_db
def test_defense_calculation_service_walls_enclosed_with_defense_buildings():
    """Test that service calculates total defense when walls are enclosed."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create buildings with defense values
    wall_building_1 = BuildingFactory(building_type=wall_type, defense_value=10)
    wall_building_2 = BuildingFactory(building_type=wall_type, defense_value=15)
    city_building = BuildingFactory(building_type=city_type, defense_value=20)

    # Create tiles with buildings
    tiles = [
        TileFactory.build(savegame=savegame, terrain=terrain, building=wall_building_1, x=0, y=0),
        TileFactory.build(savegame=savegame, terrain=terrain, building=wall_building_2, x=1, y=0),
        TileFactory.build(savegame=savegame, terrain=terrain, building=city_building, x=2, y=0),
    ]
    Tile.objects.bulk_create(tiles)

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = True

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 30

    mock_spike_malus_service = mock.Mock()
    mock_spike_malus_service.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
        spike_malus_service=mock_spike_malus_service,
    )
    result = service.process()

    # Expected: (10 + 15 + 20) base defense + 30 shape bonus + 0 spike malus = 75
    assert result == 75
    mock_enclosure_service.process.assert_called_once()
    mock_shape_bonus_service.process.assert_called_once()


@pytest.mark.django_db
def test_defense_calculation_service_base_defense_only_from_buildings():
    """Test that base defense only counts buildings with defense_value > 0."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])

    # Create buildings with various defense values
    wall_with_defense = BuildingFactory(building_type=wall_type, defense_value=25)
    wall_without_defense = BuildingFactory(building_type=wall_type, defense_value=0)

    # Create tiles with buildings
    tiles = [
        TileFactory.build(savegame=savegame, terrain=terrain, building=wall_with_defense, x=0, y=0),
        TileFactory.build(savegame=savegame, terrain=terrain, building=wall_without_defense, x=1, y=0),
        TileFactory.build(savegame=savegame, terrain=terrain, building=None, x=2, y=0),
    ]
    Tile.objects.bulk_create(tiles)

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = True

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 0

    mock_spike_malus_service = mock.Mock()
    mock_spike_malus_service.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
        spike_malus_service=mock_spike_malus_service,
    )
    result = service.process()

    # Expected: 25 base defense + 0 shape bonus + 0 spike malus = 25
    assert result == 25


@pytest.mark.django_db
def test_defense_calculation_service_multiple_same_buildings():
    """Test that multiple instances of same building all contribute to defense."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building type
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    wall_building = BuildingFactory(building_type=wall_type, defense_value=10)

    # Create multiple tiles with same building
    tiles = [TileFactory.build(savegame=savegame, terrain=terrain, building=wall_building, x=i, y=0) for i in range(5)]
    Tile.objects.bulk_create(tiles)

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = True

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 10

    mock_spike_malus_service = mock.Mock()
    mock_spike_malus_service.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
        spike_malus_service=mock_spike_malus_service,
    )
    result = service.process()

    # Expected: (10 * 5) base defense + 10 shape bonus + 0 spike malus = 60
    assert result == 60


@pytest.mark.django_db
def test_defense_calculation_service_integration_enclosed_square():
    """Test full integration with real services for enclosed square."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create enclosed square with city inside
    # W W W W W
    # W C C C W
    # W C C C W
    # W C C C W
    # W W W W W

    wall_positions = [(x, y) for y in range(5) for x in range(5) if x == 0 or x == 4 or y == 0 or y == 4]

    # Create buildings with defense values
    wall_buildings = {pos: BuildingFactory(building_type=wall_type, defense_value=10) for pos in wall_positions}
    city_building = BuildingFactory(building_type=city_type, defense_value=5)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y))
            if (x == 0 or x == 4 or y == 0 or y == 4)
            else (city_building if (x == 2 and y == 2) else None),
            x=x,
            y=y,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    # Use real services (no mocking)
    service = DefenseCalculationService(savegame=savegame)
    result = service.process()

    # Expected:
    # - 16 wall tiles * 10 defense = 160
    # - 1 city tile * 5 defense = 5
    # - Shape bonus: all 16 walls have 2 neighbors = 16 * 5 = 80
    # Total: 160 + 5 + 80 = 245
    assert result == 245


@pytest.mark.django_db
def test_defense_calculation_service_integration_not_enclosed():
    """Test full integration with real services when not enclosed."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()

    # Create building types
    wall_type = WallBuildingTypeFactory(allowed_terrains=[terrain])
    city_type = BuildingTypeFactory(is_city=True, is_wall=False, allowed_terrains=[terrain])

    # Create incomplete square with gap (not enclosed)
    # W W W W .
    # W C C C W
    # W C C C W
    # W C C C W
    # W W W W W

    wall_positions = [
        (x, y) for y in range(5) for x in range(5) if (x == 0 or x == 4 or y == 0 or y == 4) and not (x == 4 and y == 0)
    ]

    wall_buildings = {pos: BuildingFactory(building_type=wall_type, defense_value=10) for pos in wall_positions}
    city_building = BuildingFactory(building_type=city_type, defense_value=5)

    tiles = [
        TileFactory.build(
            savegame=savegame,
            terrain=terrain,
            building=wall_buildings.get((x, y))
            if ((x == 0 or x == 4 or y == 0 or y == 4) and not (x == 4 and y == 0))
            else (city_building if (x == 2 and y == 2) else None),
            x=x,
            y=y,
        )
        for y in range(5)
        for x in range(5)
    ]
    Tile.objects.bulk_create(tiles)

    # Use real services (no mocking)
    service = DefenseCalculationService(savegame=savegame)
    result = service.process()

    # Expected: 0 (not enclosed)
    assert result == 0


@pytest.mark.django_db
def test_defense_calculation_service_default_services_instantiated():
    """Test that service instantiates default services when not provided."""
    savegame = SavegameFactory.create()

    # Create service without injecting dependencies
    service = DefenseCalculationService(savegame=savegame)

    # Verify that services are instantiated
    assert service.enclosure_service is not None
    assert service.shape_bonus_service is not None
    assert service.spike_malus_service is not None
    assert hasattr(service.enclosure_service, "process")
    assert hasattr(service.shape_bonus_service, "process")
    assert hasattr(service.spike_malus_service, "process")


@pytest.mark.django_db
def test_defense_calculation_service_get_breakdown():
    """Test that get_breakdown returns detailed defense information."""
    savegame = SavegameFactory.create()

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = True

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 50

    mock_spike_malus_service = mock.Mock()
    mock_spike_malus_service.process.return_value = -20

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
        spike_malus_service=mock_spike_malus_service,
    )
    breakdown = service.get_breakdown()

    # Verify breakdown structure
    assert breakdown.is_enclosed is True
    assert breakdown.base_defense == 0
    assert breakdown.shape_bonus == 50
    assert breakdown.spike_malus == -20
    assert breakdown.potential_total == 30  # 0 + 50 + (-20)
    assert breakdown.actual_total == 30  # Same as potential since enclosed


@pytest.mark.django_db
def test_defense_calculation_service_get_breakdown_not_enclosed():
    """Test that get_breakdown shows potential defense even when not enclosed."""
    savegame = SavegameFactory.create()

    # Create mock services
    mock_enclosure_service = mock.Mock()
    mock_enclosure_service.process.return_value = False  # Not enclosed

    mock_shape_bonus_service = mock.Mock()
    mock_shape_bonus_service.process.return_value = 40

    mock_spike_malus_service = mock.Mock()
    mock_spike_malus_service.process.return_value = -10

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure_service,
        shape_bonus_service=mock_shape_bonus_service,
        spike_malus_service=mock_spike_malus_service,
    )
    breakdown = service.get_breakdown()

    # Verify breakdown structure
    assert breakdown.is_enclosed is False
    assert breakdown.base_defense == 0
    assert breakdown.shape_bonus == 40
    assert breakdown.spike_malus == -10
    assert breakdown.potential_total == 30  # 0 + 40 + (-10)
    assert breakdown.actual_total == 0  # 0 since not enclosed
