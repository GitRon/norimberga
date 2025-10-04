from apps.city.tests.factories import SavegameFactory
from apps.milestone.conditions.population import MinPopulationCondition


def test_min_population_condition_init():
    """Test MinPopulationCondition initialization."""
    condition = MinPopulationCondition(min_population=100)
    assert condition.min_population == 100


def test_min_population_condition_init_with_kwargs():
    """Test MinPopulationCondition initialization with kwargs."""
    condition = MinPopulationCondition(min_population=100)
    assert condition.min_population == 100


def test_min_population_condition_is_valid_true():
    """Test MinPopulationCondition is_valid returns True when population meets minimum."""
    condition = MinPopulationCondition(min_population=100)
    savegame = SavegameFactory.build(population=150)

    assert condition.is_valid(savegame=savegame) is True


def test_min_population_condition_is_valid_true_exact():
    """Test MinPopulationCondition is_valid returns True when population equals minimum."""
    condition = MinPopulationCondition(min_population=100)
    savegame = SavegameFactory.build(population=100)

    assert condition.is_valid(savegame=savegame) is True


def test_min_population_condition_is_valid_false():
    """Test MinPopulationCondition is_valid returns False when population below minimum."""
    condition = MinPopulationCondition(min_population=100)
    savegame = SavegameFactory.build(population=50)

    assert condition.is_valid(savegame=savegame) is False


def test_min_population_condition_is_valid_zero_population():
    """Test MinPopulationCondition is_valid with zero population."""
    condition = MinPopulationCondition(min_population=1)
    savegame = SavegameFactory.build(population=0)

    assert condition.is_valid(savegame=savegame) is False


def test_min_population_condition_is_valid_zero_minimum():
    """Test MinPopulationCondition is_valid with zero minimum."""
    condition = MinPopulationCondition(min_population=0)
    savegame = SavegameFactory.build(population=5)

    assert condition.is_valid(savegame=savegame) is True
