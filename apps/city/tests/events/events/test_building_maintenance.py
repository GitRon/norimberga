import pytest

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.events.building_maintenance import Event as BuildingMaintenanceEvent
from apps.city.models import Savegame
from apps.city.tests.factories import BuildingFactory, TileFactory


@pytest.mark.django_db
def test_building_maintenance_event_init():
    """Test BuildingMaintenanceEvent initialization and class attributes."""
    savegame, _ = Savegame.objects.get_or_create(id=1)

    event = BuildingMaintenanceEvent()

    assert event.PROBABILITY == 100
    assert event.TITLE == "Maintenance"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_building_maintenance_event_init_creates_savegame():
    """Test BuildingMaintenanceEvent creates savegame if it doesn't exist."""
    Savegame.objects.filter(id=1).delete()

    event = BuildingMaintenanceEvent()

    savegame = Savegame.objects.get(id=1)
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_building_maintenance_event_calculate_maintenance_with_buildings():
    """Test _calculate_maintenance returns correct sum with buildings."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    building1 = BuildingFactory(maintenance_costs=10)
    building2 = BuildingFactory(maintenance_costs=15)
    TileFactory(savegame=savegame, building=building1, x=10, y=10)
    TileFactory(savegame=savegame, building=building2, x=11, y=10)

    event = BuildingMaintenanceEvent()
    maintenance = event._calculate_maintenance()

    assert maintenance == 25


@pytest.mark.django_db
def test_building_maintenance_event_calculate_maintenance_no_buildings():
    """Test _calculate_maintenance returns None when no buildings exist."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    TileFactory(savegame=savegame, building=None, x=12, y=10)

    event = BuildingMaintenanceEvent()
    maintenance = event._calculate_maintenance()

    assert maintenance is None


@pytest.mark.django_db
def test_building_maintenance_event_get_probability_with_buildings():
    """Test get_probability returns base probability when buildings with maintenance exist."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    building = BuildingFactory(maintenance_costs=10)
    TileFactory(savegame=savegame, building=building, x=13, y=10)

    event = BuildingMaintenanceEvent()
    probability = event.get_probability()

    assert probability == 100


@pytest.mark.django_db
def test_building_maintenance_event_get_probability_no_buildings():
    """Test get_probability returns 0 when no buildings with maintenance exist."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    TileFactory(savegame=savegame, building=None, x=14, y=10)

    event = BuildingMaintenanceEvent()
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_building_maintenance_event_get_probability_zero_maintenance():
    """Test get_probability returns 0 when buildings have no maintenance costs."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    building = BuildingFactory(maintenance_costs=0)
    TileFactory(savegame=savegame, building=building, x=15, y=10)

    event = BuildingMaintenanceEvent()
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_building_maintenance_event_get_effects():
    """Test get_effects returns DecreaseCoins effect with correct maintenance amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    building1 = BuildingFactory(maintenance_costs=8)
    building2 = BuildingFactory(maintenance_costs=12)
    TileFactory(savegame=savegame, building=building1, x=16, y=10)
    TileFactory(savegame=savegame, building=building2, x=17, y=10)

    event = BuildingMaintenanceEvent()
    effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], DecreaseCoins)
    assert effects[0].coins == 20


@pytest.mark.django_db
def test_building_maintenance_event_get_effects_no_maintenance():
    """Test get_effects returns DecreaseCoins effect with None when no maintenance."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    TileFactory(savegame=savegame, building=None, x=18, y=10)

    event = BuildingMaintenanceEvent()
    effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], DecreaseCoins)
    assert effects[0].coins is None


@pytest.mark.django_db
def test_building_maintenance_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    building = BuildingFactory(maintenance_costs=25)
    TileFactory(savegame=savegame, building=building, x=19, y=10)

    event = BuildingMaintenanceEvent()
    verbose_text = event.get_verbose_text()

    expected_text = "The treasury was set back by 25 coin to maintain the citys buildings."
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_building_maintenance_event_get_verbose_text_none_maintenance():
    """Test get_verbose_text handles None maintenance correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    TileFactory(savegame=savegame, building=None, x=20, y=10)

    event = BuildingMaintenanceEvent()
    verbose_text = event.get_verbose_text()

    expected_text = "The treasury was set back by None coin to maintain the citys buildings."
    assert verbose_text == expected_text
