import pytest

from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.events.events.building_taxes import Event as BuildingTaxesEvent
from apps.city.models import Savegame
from apps.city.tests.factories import BuildingFactory, TileFactory


@pytest.mark.django_db
def test_building_taxes_event_init():
    """Test BuildingTaxesEvent initialization and class attributes."""
    savegame, _ = Savegame.objects.get_or_create(id=1)

    event = BuildingTaxesEvent()

    assert event.PROBABILITY == 100
    assert event.TITLE == "Taxes"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_building_taxes_event_init_creates_savegame():
    """Test BuildingTaxesEvent creates savegame if it doesn't exist."""
    Savegame.objects.filter(id=1).delete()

    event = BuildingTaxesEvent()

    savegame = Savegame.objects.get(id=1)
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_building_taxes_event_calculate_taxes_with_buildings():
    """Test _calculate_taxes returns correct sum with buildings."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building1 = BuildingFactory(taxes=20)
    building2 = BuildingFactory(taxes=30)
    TileFactory(savegame=savegame, building=building1, x=30, y=10)
    TileFactory(savegame=savegame, building=building2, x=31, y=10)

    event = BuildingTaxesEvent()
    taxes = event._calculate_taxes()

    assert taxes == 50


@pytest.mark.django_db
def test_building_taxes_event_calculate_taxes_no_buildings():
    """Test _calculate_taxes returns None when no buildings exist."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    TileFactory(savegame=savegame, building=None, x=32, y=10)

    event = BuildingTaxesEvent()
    taxes = event._calculate_taxes()

    assert taxes is None


@pytest.mark.django_db
def test_building_taxes_event_get_probability_with_tax_buildings():
    """Test get_probability returns base probability when buildings with taxes exist."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building = BuildingFactory(taxes=15)
    TileFactory(savegame=savegame, building=building, x=33, y=10)

    event = BuildingTaxesEvent()
    probability = event.get_probability()

    assert probability == 100


@pytest.mark.django_db
def test_building_taxes_event_get_probability_no_buildings():
    """Test get_probability returns 0 when no buildings exist."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    TileFactory(savegame=savegame, building=None, x=34, y=10)

    event = BuildingTaxesEvent()
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_building_taxes_event_get_probability_zero_taxes():
    """Test get_probability returns 0 when buildings have no taxes."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building = BuildingFactory(taxes=0)
    TileFactory(savegame=savegame, building=building, x=35, y=10)

    event = BuildingTaxesEvent()
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_building_taxes_event_get_effects():
    """Test get_effects returns IncreaseCoins effect with correct tax amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building1 = BuildingFactory(taxes=18)
    building2 = BuildingFactory(taxes=22)
    TileFactory(savegame=savegame, building=building1, x=36, y=10)
    TileFactory(savegame=savegame, building=building2, x=37, y=10)

    event = BuildingTaxesEvent()
    effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], IncreaseCoins)
    assert effects[0].coins == 40


@pytest.mark.django_db
def test_building_taxes_event_get_effects_no_taxes():
    """Test get_effects returns IncreaseCoins effect with None when no taxes."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    TileFactory(savegame=savegame, building=None, x=38, y=10)

    event = BuildingTaxesEvent()
    effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], IncreaseCoins)
    assert effects[0].coins is None


@pytest.mark.django_db
def test_building_taxes_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building = BuildingFactory(taxes=45)
    TileFactory(savegame=savegame, building=building, x=39, y=10)

    event = BuildingTaxesEvent()
    verbose_text = event.get_verbose_text()

    expected_text = "Your loyal subjects were delighted to pay their fair amount of 45 coins as taxes to your city."
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_building_taxes_event_get_verbose_text_none_taxes():
    """Test get_verbose_text handles None taxes correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1)
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    TileFactory(savegame=savegame, building=None, x=40, y=10)

    event = BuildingTaxesEvent()
    verbose_text = event.get_verbose_text()

    expected_text = "Your loyal subjects were delighted to pay their fair amount of None coins as taxes to your city."
    assert verbose_text == expected_text
