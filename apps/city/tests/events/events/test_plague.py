from unittest import mock

import pytest

from apps.city.events.effects.savegame.decrease_population_relative import DecreasePopulationRelative
from apps.city.events.events.plague import Event as PlagueEvent
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_plague_event_init():
    """Test PlagueEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 15

        event = PlagueEvent(savegame=savegame)

        assert event.PROBABILITY == 5
        assert event.TITLE == "Plague"
        assert event.savegame.id == savegame.id
        assert event.lost_population_percentage == 0.15


@pytest.mark.django_db
def test_plague_event_init_creates_savegame():
    """Test PlagueEvent accepts a savegame parameter."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 20

        event = PlagueEvent(savegame=savegame)

        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_plague_event_get_probability_with_population():
    """Test get_probability returns base probability when population exists."""
    savegame = SavegameFactory(population=50)
    savegame.save()

    with mock.patch("apps.city.events.events.plague.random.randint"):
        event = PlagueEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 5


@pytest.mark.django_db
def test_plague_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)
    savegame.save()

    with mock.patch("apps.city.events.events.plague.random.randint"):
        event = PlagueEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_plague_event_get_effects():
    """Test get_effects returns DecreasePopulationRelative effect."""
    savegame = SavegameFactory(population=200)

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 18

        event = PlagueEvent(savegame=savegame)
        effects = event.get_effects()

        assert len(effects) == 1
        assert isinstance(effects[0], DecreasePopulationRelative)
        assert effects[0].lost_population == 0.18


@pytest.mark.django_db
def test_plague_event_get_verbose_text_minimum_percentage():
    """Test get_verbose_text returns correct description for minimum percentage."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 10

        event = PlagueEvent(savegame=savegame)
        verbose_text = event.get_verbose_text()

        expected_text = (
            "A horrific plague hit the city in its most vulnerable time. 1% of the population "
            "died a tragic and slow death."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_plague_event_get_verbose_text_maximum_percentage():
    """Test get_verbose_text returns correct description for maximum percentage."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 25

        event = PlagueEvent(savegame=savegame)
        verbose_text = event.get_verbose_text()

        expected_text = (
            "A horrific plague hit the city in its most vulnerable time. 2% of the population "
            "died a tragic and slow death."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_plague_event_get_verbose_text_mid_percentage():
    """Test get_verbose_text returns correct description for mid-range percentage."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 17

        event = PlagueEvent(savegame=savegame)
        verbose_text = event.get_verbose_text()

        expected_text = (
            "A horrific plague hit the city in its most vulnerable time. 2% of the population "
            "died a tragic and slow death."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_plague_event_random_range():
    """Test that random.randint is called with correct range."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 15

        PlagueEvent(savegame=savegame)

        mock_randint.assert_called_once_with(10, 25)


@pytest.mark.django_db
def test_plague_event_percentage_calculation():
    """Test that percentage is correctly calculated from random value."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.plague.random.randint") as mock_randint:
        mock_randint.return_value = 22

        event = PlagueEvent(savegame=savegame)

        assert event.lost_population_percentage == 0.22
