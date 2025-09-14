import pytest

from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.models import Savegame


@pytest.mark.django_db
def test_decrease_population_absolute_init():
    """Test DecreasePopulationAbsolute initialization with parameters."""
    effect = DecreasePopulationAbsolute(lost_population=25)

    assert effect.lost_population == 25


@pytest.mark.django_db
def test_decrease_population_absolute_process_normal_decrease():
    """Test process decreases population by specified amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 100})
    savegame.population = 100
    savegame.save()
    effect = DecreasePopulationAbsolute(lost_population=30)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 70


@pytest.mark.django_db
def test_decrease_population_absolute_process_minimum_zero():
    """Test process does not decrease population below zero."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 20})
    savegame.population = 20
    savegame.save()
    effect = DecreasePopulationAbsolute(lost_population=35)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_absolute_process_exact_zero():
    """Test process handles exact zero population correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 40})
    savegame.population = 40
    savegame.save()
    effect = DecreasePopulationAbsolute(lost_population=40)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_absolute_process_creates_savegame():
    """Test process creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()
    effect = DecreasePopulationAbsolute(lost_population=10)

    effect.process()

    savegame = Savegame.objects.get(id=1)
    assert savegame.population == max(0 - 10, 0)  # Default population (0) - lost_population, min 0


@pytest.mark.django_db
def test_decrease_population_absolute_process_zero_decrease():
    """Test process with zero decrease amount."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 80})
    savegame.population = 80
    savegame.save()
    effect = DecreasePopulationAbsolute(lost_population=0)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 80