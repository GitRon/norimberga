from unittest import mock

import pytest

from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_defense_calculation_wall_at_full_hp_contributes_full_defense():
    """Test wall tile at 100% HP contributes full defense_value."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1, defense_value=50)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    mock_enclosure = mock.Mock()
    mock_enclosure.process.return_value = True
    mock_shape = mock.Mock()
    mock_shape.process.return_value = 0
    mock_spike = mock.Mock()
    mock_spike.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure,
        shape_bonus_service=mock_shape,
        spike_malus_service=mock_spike,
    )
    result = service.process()

    assert result == 50


@pytest.mark.django_db
def test_defense_calculation_wall_at_half_hp_contributes_half_defense():
    """Test wall tile at 50% HP contributes half its defense_value."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1, defense_value=50)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=50)

    mock_enclosure = mock.Mock()
    mock_enclosure.process.return_value = True
    mock_shape = mock.Mock()
    mock_shape.process.return_value = 0
    mock_spike = mock.Mock()
    mock_spike.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure,
        shape_bonus_service=mock_shape,
        spike_malus_service=mock_spike,
    )
    result = service.process()

    assert result == 25


@pytest.mark.django_db
def test_defense_calculation_non_wall_unaffected_by_hp():
    """Test non-wall buildings contribute full defense regardless of wall_hitpoints."""
    from apps.city.tests.factories import BuildingTypeFactory

    savegame = SavegameFactory.create()
    city_type = BuildingTypeFactory.create(is_city=True, is_wall=False)
    building = BuildingFactory.create(building_type=city_type, defense_value=30)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=None)

    mock_enclosure = mock.Mock()
    mock_enclosure.process.return_value = True
    mock_shape = mock.Mock()
    mock_shape.process.return_value = 0
    mock_spike = mock.Mock()
    mock_spike.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure,
        shape_bonus_service=mock_shape,
        spike_malus_service=mock_spike,
    )
    result = service.process()

    assert result == 30


@pytest.mark.django_db
def test_defense_calculation_wall_with_none_hitpoints_contributes_full_defense():
    """Test wall tile with wall_hitpoints=None contributes full defense (no HP data = full health)."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1, defense_value=50)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=None)

    mock_enclosure = mock.Mock()
    mock_enclosure.process.return_value = True
    mock_shape = mock.Mock()
    mock_shape.process.return_value = 0
    mock_spike = mock.Mock()
    mock_spike.process.return_value = 0

    service = DefenseCalculationService(
        savegame=savegame,
        enclosure_service=mock_enclosure,
        shape_bonus_service=mock_shape,
        spike_malus_service=mock_spike,
    )
    result = service.process()

    assert result == 50
