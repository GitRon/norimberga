from apps.city.tests.factories import SavegameFactory
from apps.milestone.conditions.population import MinPopulationCondition


def test_min_population_condition_init():
    """Test MinPopulationCondition initialization."""
    savegame = SavegameFactory.build()
    condition = MinPopulationCondition(savegame=savegame, value=100)
    assert condition.value == 100


def test_min_population_condition_is_valid_true():
    """Test MinPopulationCondition is_valid returns True when population meets minimum."""
    savegame = SavegameFactory.build(population=150)
    condition = MinPopulationCondition(savegame=savegame, value=100)

    assert condition.is_valid() is True


def test_min_population_condition_is_valid_true_exact():
    """Test MinPopulationCondition is_valid returns True when population equals minimum."""
    savegame = SavegameFactory.build(population=100)
    condition = MinPopulationCondition(savegame=savegame, value=100)

    assert condition.is_valid() is True


def test_min_population_condition_is_valid_false():
    """Test MinPopulationCondition is_valid returns False when population below minimum."""
    savegame = SavegameFactory.build(population=50)
    condition = MinPopulationCondition(savegame=savegame, value=100)

    assert condition.is_valid() is False


def test_min_population_condition_is_valid_zero_population():
    """Test MinPopulationCondition is_valid with zero population."""
    savegame = SavegameFactory.build(population=0)
    condition = MinPopulationCondition(savegame=savegame, value=1)

    assert condition.is_valid() is False


def test_min_population_condition_is_valid_zero_minimum():
    """Test MinPopulationCondition is_valid with zero minimum."""
    savegame = SavegameFactory.build(population=5)
    condition = MinPopulationCondition(savegame=savegame, value=0)

    assert condition.is_valid() is True
