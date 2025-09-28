from unittest import mock

import pytest

from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.events.riot import Event as RiotEvent
from apps.city.models import Savegame


@pytest.mark.django_db
def test_riot_event_init():
    """Test RiotEvent initialization and class attributes."""
    # Delete any existing savegame and create fresh one
    Savegame.objects.filter(id=1).delete()
    savegame = Savegame.objects.create(id=1, population=100)

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 7

        event = RiotEvent()

        assert event.PROBABILITY == 100
        assert event.TITLE == "Riots"
        assert event.savegame.id == savegame.id
        assert event.initial_population == 100
        assert event.lost_population == 8  # ceil((7/100) * 100) = 8 due to floating point precision


@pytest.mark.django_db
def test_riot_event_init_creates_savegame():
    """Test RiotEvent creates savegame if it doesn't exist."""
    Savegame.objects.filter(id=1).delete()

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 8

        event = RiotEvent()

        savegame = Savegame.objects.get(id=1)
        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_riot_event_lost_population_calculation():
    """Test lost_population calculation with different percentages."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 200})
    savegame.population = 200
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 6

        event = RiotEvent()

        # ceil((6/100) * 200) = ceil(12) = 12
        assert event.lost_population == 12


@pytest.mark.django_db
def test_riot_event_lost_population_small_population():
    """Test lost_population calculation with small population."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 10})
    savegame.population = 10
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 5

        event = RiotEvent()

        # ceil((5/100) * 10) = ceil(0.5) = 1
        assert event.lost_population == 1


@pytest.mark.django_db
def test_riot_event_get_probability_with_population_and_unrest():
    """Test get_probability calculation with population and unrest."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100, "unrest": 50})
    savegame.population = 100
    savegame.unrest = 50
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint"):
        event = RiotEvent()
        probability = event.get_probability()

        # 100 * 50 / 100 = 50
        assert probability == 50


@pytest.mark.django_db
def test_riot_event_get_probability_high_unrest():
    """Test get_probability calculation with high unrest."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100, "unrest": 80})
    savegame.population = 100
    savegame.unrest = 80
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint"):
        event = RiotEvent()
        probability = event.get_probability()

        # 100 * 80 / 100 = 80
        assert probability == 80


@pytest.mark.django_db
def test_riot_event_get_probability_zero_unrest():
    """Test get_probability returns 0 when unrest is zero."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100, "unrest": 0})
    savegame.population = 100
    savegame.unrest = 0
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint"):
        event = RiotEvent()
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_riot_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 0, "unrest": 50})
    savegame.population = 0
    savegame.unrest = 50
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint"):
        event = RiotEvent()
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_riot_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 150})
    savegame.population = 150
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 8

        event = RiotEvent()
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreasePopulationAbsolute)
        assert effect.lost_population == 12  # ceil((8/100) * 150) = 12


@pytest.mark.django_db
def test_riot_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 100})
    savegame.population = 100
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 6

        event = RiotEvent()
        initial_population = event.initial_population

        # Simulate effect processing (decrease population)
        lost_population = event.lost_population
        savegame.population = savegame.population - lost_population
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{initial_population - savegame.population} human lives."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_riot_event_random_range():
    """Test that random.randint is called with correct range."""
    Savegame.objects.get_or_create(id=1, defaults={"population": 100})

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 7

        RiotEvent()

        mock_randint.assert_called_once_with(5, 10)


@pytest.mark.django_db
def test_riot_event_fractional_calculation():
    """Test lost_population handles fractional calculations correctly."""
    savegame, _ = Savegame.objects.get_or_create(id=1, defaults={"population": 33})
    savegame.population = 33
    savegame.save()

    with mock.patch("apps.city.events.events.riot.random.randint") as mock_randint:
        mock_randint.return_value = 5

        event = RiotEvent()

        # ceil((5/100) * 33) = ceil(1.65) = 2
        assert event.lost_population == 2
