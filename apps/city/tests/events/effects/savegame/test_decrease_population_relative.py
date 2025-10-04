import pytest

from apps.city.events.effects.savegame.decrease_population_relative import DecreasePopulationRelative
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_decrease_population_relative_init():
    """Test DecreasePopulationRelative initialization with parameters."""
    effect = DecreasePopulationRelative(lost_population_percentage=0.25)

    assert effect.lost_population == 0.25


@pytest.mark.django_db
def test_decrease_population_relative_process_percentage_decrease():
    """Test process decreases population by specified percentage."""
    savegame = SavegameFactory(population=100)
    effect = DecreasePopulationRelative(lost_population_percentage=0.3)  # 30% decrease

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.population == 70  # 100 * (1 - 0.3) = 70


@pytest.mark.django_db
def test_decrease_population_relative_process_rounding():
    """Test process handles rounding correctly."""
    savegame = SavegameFactory(population=77)
    effect = DecreasePopulationRelative(lost_population_percentage=0.1)  # 10% decrease

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.population == 69  # round(77 * 0.9) = round(69.3) = 69


@pytest.mark.django_db
def test_decrease_population_relative_process_minimum_zero():
    """Test process does not decrease population below zero."""
    savegame = SavegameFactory(population=50)
    effect = DecreasePopulationRelative(lost_population_percentage=1.5)  # 150% decrease

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_relative_process_complete_loss():
    """Test process handles 100% population loss."""
    savegame = SavegameFactory(population=80)
    effect = DecreasePopulationRelative(lost_population_percentage=1.0)  # 100% decrease

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_relative_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(population=0)
    effect = DecreasePopulationRelative(lost_population_percentage=0.2)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    expected_population = max(round(0 * (1 - 0.2)), 0)  # Default population (0) * (1 - percentage)
    assert savegame.population == expected_population


@pytest.mark.django_db
def test_decrease_population_relative_process_zero_percentage():
    """Test process with zero percentage decrease."""
    savegame = SavegameFactory(population=120)
    effect = DecreasePopulationRelative(lost_population_percentage=0.0)

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.population == 120


@pytest.mark.django_db
def test_decrease_population_relative_process_small_percentage():
    """Test process with very small percentage."""
    savegame = SavegameFactory(population=1000)
    effect = DecreasePopulationRelative(lost_population_percentage=0.05)  # 5% decrease

    effect.process(savegame=savegame)

    savegame.refresh_from_db()
    assert savegame.population == 950  # 1000 * 0.95 = 950
