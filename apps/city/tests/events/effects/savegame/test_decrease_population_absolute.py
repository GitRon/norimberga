import pytest

from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_decrease_population_absolute_init():
    """Test DecreasePopulationAbsolute initialization with parameters."""
    effect = DecreasePopulationAbsolute(lost_population=25)

    assert effect.lost_population == 25


@pytest.mark.django_db
def test_decrease_population_absolute_process_normal_decrease():
    """Test process decreases population by specified amount."""
    savegame = SavegameFactory(population=100)
    effect = DecreasePopulationAbsolute(lost_population=30)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.population == 70


@pytest.mark.django_db
def test_decrease_population_absolute_process_minimum_zero():
    """Test process does not decrease population below zero."""
    savegame = SavegameFactory(population=20)
    effect = DecreasePopulationAbsolute(lost_population=35)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_absolute_process_exact_zero():
    """Test process handles exact zero population correctly."""
    savegame = SavegameFactory(population=40)
    effect = DecreasePopulationAbsolute(lost_population=40)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_absolute_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(population=0)
    effect = DecreasePopulationAbsolute(lost_population=10)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.population == max(0 - 10, 0)  # Default population (0) - lost_population, min 0


@pytest.mark.django_db
def test_decrease_population_absolute_process_zero_decrease():
    """Test process with zero decrease amount."""
    savegame = SavegameFactory(population=80)
    effect = DecreasePopulationAbsolute(lost_population=0)

    effect.process(savegame)

    savegame.refresh_from_db()
    assert savegame.population == 80
