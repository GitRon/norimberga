import pytest

from apps.city.events.effects.savegame.increase_population_absolute import IncreasePopulationAbsolute
from apps.city.events.events.population_increase import Event as PopulationIncreaseEvent
from apps.city.tests.factories import BuildingFactory, HouseBuildingTypeFactory, SavegameFactory, TileFactory


@pytest.mark.django_db
def test_population_increase_event_init():
    """Test PopulationIncreaseEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    event = PopulationIncreaseEvent(savegame=savegame)

    assert event.PROBABILITY == 100
    assert event.TITLE == "Population increase"
    assert event.YEARLY_POP_INCREASE_FACTOR == 0.15
    assert event.savegame.id == savegame.id
    assert event.initial_population == 100
    assert event.new_population == 15  # ceil(100 * 0.15) = 15


@pytest.mark.django_db
def test_population_increase_event_init_creates_savegame():
    """Test PopulationIncreaseEvent creates savegame if it doesn't exist."""
    savegame = SavegameFactory()

    event = PopulationIncreaseEvent(savegame=savegame)

    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_population_increase_event_init_small_population():
    """Test PopulationIncreaseEvent handles small population correctly."""
    savegame = SavegameFactory(population=10)
    savegame.save()

    event = PopulationIncreaseEvent(savegame=savegame)

    assert event.new_population == 2  # max(ceil(10 * 0.15), 1) = max(2, 1) = 2


@pytest.mark.django_db
def test_population_increase_event_init_zero_population():
    """Test PopulationIncreaseEvent handles zero population correctly."""
    savegame = SavegameFactory(population=0)
    savegame.save()

    event = PopulationIncreaseEvent(savegame=savegame)

    assert event.new_population == 1  # max(ceil(0 * 0.15), 1) = max(0, 1) = 1


@pytest.mark.django_db
def test_population_increase_event_get_probability_space_available():
    """Test get_probability returns base probability when housing space is available."""
    savegame = SavegameFactory(population=50)
    savegame.save()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=100)
    TileFactory(savegame=savegame, building=building, x=60, y=10)

    event = PopulationIncreaseEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 100


@pytest.mark.django_db
def test_population_increase_event_get_probability_no_space():
    """Test get_probability returns 0 when population exceeds housing capacity."""
    savegame = SavegameFactory(population=120)
    savegame.save()
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=100)
    TileFactory(savegame=savegame, building=building, x=61, y=10)

    event = PopulationIncreaseEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_population_increase_event_get_probability_exact_capacity():
    """Test get_probability returns 0 when population equals housing capacity."""
    savegame = SavegameFactory(population=100)
    building_type = HouseBuildingTypeFactory()
    building = BuildingFactory(building_type=building_type, housing_space=100)
    TileFactory(savegame=savegame, building=building, x=62, y=10)

    event = PopulationIncreaseEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_population_increase_event_get_effects():
    """Test get_effects returns IncreasePopulationAbsolute effect."""
    savegame = SavegameFactory(population=80)
    savegame.save()

    event = PopulationIncreaseEvent(savegame=savegame)
    effects = event.get_effects()

    assert len(effects) == 1
    assert isinstance(effects[0], IncreasePopulationAbsolute)
    assert effects[0].new_population == 12  # ceil(80 * 0.15) = 12


@pytest.mark.django_db
def test_population_increase_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=60)
    savegame.save()

    event = PopulationIncreaseEvent(savegame=savegame)
    verbose_text = event.get_verbose_text()

    expected_text = "Your fertile city welcomes 9 new inhabitants."  # ceil(60 * 0.15) = 9
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_population_increase_event_large_population():
    """Test PopulationIncreaseEvent with large population."""
    savegame = SavegameFactory(population=1000)
    savegame.save()

    event = PopulationIncreaseEvent(savegame=savegame)

    assert event.new_population == 150  # ceil(1000 * 0.15) = 150


@pytest.mark.django_db
def test_population_increase_event_fractional_calculation():
    """Test PopulationIncreaseEvent handles fractional calculations correctly."""
    savegame = SavegameFactory(population=33)
    savegame.save()

    event = PopulationIncreaseEvent(savegame=savegame)

    # ceil(33 * 0.15) = ceil(4.95) = 5
    assert event.new_population == 5
