import pytest

from apps.city.events.effects.savegame.increase_population_absolute import IncreasePopulationAbsolute
from apps.city.events.events.population_increase import Event as PopulationIncreaseEvent
from apps.city.models import Savegame
from apps.city.tests.factories import BuildingFactory, HouseBuildingTypeFactory, TileFactory


@pytest.mark.django_db
def test_population_increase_event_init():
    """Test PopulationIncreaseEvent initialization and class attributes."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100})
    savegame.population = 100
    savegame.save()

    event = PopulationIncreaseEvent()

    assert event.PROBABILITY == 100
    assert event.TITLE == "Population increase"
    assert event.YEARLY_POP_INCREASE_FACTOR == 0.05
    assert event.savegame.id == savegame.id
    assert event.initial_population == 100
    assert event.new_population == 5  # ceil(100 * 0.05) = 5


@pytest.mark.django_db
def test_population_increase_event_init_creates_savegame():
    """Test PopulationIncreaseEvent creates savegame if it doesn't exist."""
    Savegame.objects.filter(id=1).delete()

    event = PopulationIncreaseEvent()

    savegame = Savegame.objects.get(id=1)
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_population_increase_event_init_small_population():
    """Test PopulationIncreaseEvent handles small population correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 10})
    savegame.population = 10
    savegame.save()

    event = PopulationIncreaseEvent()

    assert event.new_population == 1  # max(ceil(10 * 0.05), 1) = max(1, 1) = 1


@pytest.mark.django_db
def test_population_increase_event_init_zero_population():
    """Test PopulationIncreaseEvent handles zero population correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 0})
    savegame.population = 0
    savegame.save()

    event = PopulationIncreaseEvent()

    assert event.new_population == 1  # max(ceil(0 * 0.05), 1) = max(0, 1) = 1


@pytest.mark.django_db
def test_population_increase_event_get_probability_space_available():
    """Test get_probability returns base probability when housing space is available."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 50})
    savegame.population = 50
    savegame.save()
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=100)
    TileFactory(savegame=savegame, building=building, x=60, y=10)

    event = PopulationIncreaseEvent()
    probability = event.get_probability()

    assert probability == 100


@pytest.mark.django_db
def test_population_increase_event_get_probability_no_space():
    """Test get_probability returns 0 when population exceeds housing capacity."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 120})
    savegame.population = 120
    savegame.save()
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=100)
    TileFactory(savegame=savegame, building=building, x=61, y=10)

    event = PopulationIncreaseEvent()
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_population_increase_event_get_probability_exact_capacity():
    """Test get_probability returns 0 when population equals housing capacity."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100})
    savegame.population = 100
    savegame.save()
    # Clear any existing tiles for this savegame
    savegame.tiles.all().delete()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=100)
    TileFactory(savegame=savegame, building=building, x=62, y=10)

    event = PopulationIncreaseEvent()
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_population_increase_event_get_effects():
    """Test get_effects returns IncreasePopulationAbsolute effect."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 80})
    savegame.population = 80
    savegame.save()

    event = PopulationIncreaseEvent()
    effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], IncreasePopulationAbsolute)
    assert effects[0].new_population == 4  # ceil(80 * 0.05) = 4


@pytest.mark.django_db
def test_population_increase_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 60})
    savegame.population = 60
    savegame.save()

    event = PopulationIncreaseEvent()
    verbose_text = event.get_verbose_text()

    expected_text = "Your fertile city welcomes 3 new inhabitants."  # ceil(60 * 0.05) = 3
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_population_increase_event_large_population():
    """Test PopulationIncreaseEvent with large population."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 1000})
    savegame.population = 1000
    savegame.save()

    event = PopulationIncreaseEvent()

    assert event.new_population == 50  # ceil(1000 * 0.05) = 50


@pytest.mark.django_db
def test_population_increase_event_fractional_calculation():
    """Test PopulationIncreaseEvent handles fractional calculations correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 33})
    savegame.population = 33
    savegame.save()

    event = PopulationIncreaseEvent()

    # ceil(33 * 0.05) = ceil(1.65) = 2
    assert event.new_population == 2
