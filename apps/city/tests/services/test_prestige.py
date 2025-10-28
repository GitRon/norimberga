import pytest

from apps.city.services.prestige import PrestigeCalculationService
from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_prestige_calculation_no_buildings():
    """Test prestige calculation with no buildings."""
    savegame = SavegameFactory.create()
    service = PrestigeCalculationService(savegame=savegame)

    result = service.process()

    assert result == 0


@pytest.mark.django_db
def test_prestige_calculation_buildings_without_prestige():
    """Test prestige calculation with buildings that have no prestige (level 1)."""
    savegame = SavegameFactory.create()
    building_without_prestige = BuildingFactory.create(level=1, prestige=0)
    TileFactory.create(savegame=savegame, building=building_without_prestige)

    service = PrestigeCalculationService(savegame=savegame)
    result = service.process()

    assert result == 0


@pytest.mark.django_db
def test_prestige_calculation_single_building_with_prestige():
    """Test prestige calculation with a single building that has prestige."""
    savegame = SavegameFactory.create()
    building_with_prestige = BuildingFactory.create(level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building_with_prestige)

    service = PrestigeCalculationService(savegame=savegame)
    result = service.process()

    assert result == 5


@pytest.mark.django_db
def test_prestige_calculation_multiple_buildings():
    """Test prestige calculation with multiple buildings with different prestige values."""
    savegame = SavegameFactory.create()
    building1 = BuildingFactory.create(level=2, prestige=3)
    building2 = BuildingFactory.create(level=3, prestige=8)
    building3 = BuildingFactory.create(level=2, prestige=2)
    building4 = BuildingFactory.create(level=1, prestige=0)

    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)
    TileFactory.create(savegame=savegame, building=building3)
    TileFactory.create(savegame=savegame, building=building4)

    service = PrestigeCalculationService(savegame=savegame)
    result = service.process()

    assert result == 13


@pytest.mark.django_db
def test_prestige_calculation_tiles_without_buildings():
    """Test prestige calculation with tiles that have no buildings."""
    savegame = SavegameFactory.create()
    TileFactory.create(savegame=savegame, building=None)
    TileFactory.create(savegame=savegame, building=None)

    service = PrestigeCalculationService(savegame=savegame)
    result = service.process()

    assert result == 0


@pytest.mark.django_db
def test_prestige_calculation_mixed_tiles():
    """Test prestige calculation with mix of tiles with and without buildings."""
    savegame = SavegameFactory.create()
    building_with_prestige = BuildingFactory.create(level=3, prestige=10)

    TileFactory.create(savegame=savegame, building=building_with_prestige)
    TileFactory.create(savegame=savegame, building=None)
    TileFactory.create(savegame=savegame, building=None)

    service = PrestigeCalculationService(savegame=savegame)
    result = service.process()

    assert result == 10


@pytest.mark.django_db
def test_prestige_calculation_only_specific_savegame():
    """Test that prestige calculation only considers buildings from the specified savegame."""
    savegame1 = SavegameFactory.create()
    savegame2 = SavegameFactory.create()

    building1 = BuildingFactory.create(level=2, prestige=5)
    building2 = BuildingFactory.create(level=3, prestige=10)

    TileFactory.create(savegame=savegame1, building=building1)
    TileFactory.create(savegame=savegame2, building=building2)

    service1 = PrestigeCalculationService(savegame=savegame1)
    service2 = PrestigeCalculationService(savegame=savegame2)

    result1 = service1.process()
    result2 = service2.process()

    assert result1 == 5
    assert result2 == 10
