import pytest

from apps.city.events.effects.savegame.decrease_population_relative import DecreasePopulationRelative
from apps.city.models import Savegame


@pytest.mark.django_db
def test_decrease_population_relative_init():
    """Test DecreasePopulationRelative initialization with parameters."""
    effect = DecreasePopulationRelative(lost_population_percentage=0.25)

    assert effect.lost_population == 0.25


@pytest.mark.django_db
def test_decrease_population_relative_process_percentage_decrease():
    """Test process decreases population by specified percentage."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 100})
    savegame.population = 100
    savegame.save()
    effect = DecreasePopulationRelative(lost_population_percentage=0.3)  # 30% decrease

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 70  # 100 * (1 - 0.3) = 70


@pytest.mark.django_db
def test_decrease_population_relative_process_rounding():
    """Test process handles rounding correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 77})
    savegame.population = 77
    savegame.save()
    effect = DecreasePopulationRelative(lost_population_percentage=0.1)  # 10% decrease

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 69  # round(77 * 0.9) = round(69.3) = 69


@pytest.mark.django_db
def test_decrease_population_relative_process_minimum_zero():
    """Test process does not decrease population below zero."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 50})
    savegame.population = 50
    savegame.save()
    effect = DecreasePopulationRelative(lost_population_percentage=1.5)  # 150% decrease

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_relative_process_complete_loss():
    """Test process handles 100% population loss."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 80})
    savegame.population = 80
    savegame.save()
    effect = DecreasePopulationRelative(lost_population_percentage=1.0)  # 100% decrease

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 0


@pytest.mark.django_db
def test_decrease_population_relative_process_creates_savegame():
    """Test process creates savegame if it doesn't exist."""
    # Ensure no savegame exists
    Savegame.objects.filter(id=1).delete()
    effect = DecreasePopulationRelative(lost_population_percentage=0.2)

    effect.process()

    savegame = Savegame.objects.get(id=1)
    expected_population = max(round(0 * (1 - 0.2)), 0)  # Default population (0) * (1 - percentage)
    assert savegame.population == expected_population


@pytest.mark.django_db
def test_decrease_population_relative_process_zero_percentage():
    """Test process with zero percentage decrease."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 120})
    savegame.population = 120
    savegame.save()
    effect = DecreasePopulationRelative(lost_population_percentage=0.0)

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 120


@pytest.mark.django_db
def test_decrease_population_relative_process_small_percentage():
    """Test process with very small percentage."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={'population': 1000})
    savegame.population = 1000
    savegame.save()
    effect = DecreasePopulationRelative(lost_population_percentage=0.05)  # 5% decrease

    effect.process()

    savegame.refresh_from_db()
    assert savegame.population == 950  # 1000 * 0.95 = 950