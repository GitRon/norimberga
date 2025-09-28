from unittest import mock

import pytest

from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.events.events.wanted_criminal import Event as WantedCriminalEvent


@pytest.mark.django_db
def test_wanted_criminal_event_init():
    """Test WantedCriminalEvent initialization and class attributes."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 150

        event = WantedCriminalEvent()

        assert event.PROBABILITY == 20
        assert event.TITLE == "Wanted criminal"
        assert event.bounty == 150


@pytest.mark.django_db
def test_wanted_criminal_event_prepare_effect_increase_coins():
    """Test _prepare_effect_increase_coins returns correct effect."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 250

        event = WantedCriminalEvent()
        effect = event._prepare_effect_increase_coins()

        assert isinstance(effect, IncreaseCoins)
        assert effect.coins == 250


@pytest.mark.django_db
def test_wanted_criminal_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 200

        event = WantedCriminalEvent()
        verbose_text = event.get_verbose_text()

        expected_text = (
            "The magistrate caught a wanted criminal. The malefactor was handed over to the Kings guard, rewarding "
            "you with 200 coin."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_wanted_criminal_event_random_range():
    """Test that random.randint is called with correct range."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 175

        WantedCriminalEvent()

        mock_randint.assert_called_once_with(100, 300)


@pytest.mark.django_db
def test_wanted_criminal_event_minimum_bounty():
    """Test WantedCriminalEvent with minimum bounty."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 100

        event = WantedCriminalEvent()

        assert event.bounty == 100


@pytest.mark.django_db
def test_wanted_criminal_event_maximum_bounty():
    """Test WantedCriminalEvent with maximum bounty."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 300

        event = WantedCriminalEvent()

        assert event.bounty == 300


@pytest.mark.django_db
def test_wanted_criminal_event_mid_range_bounty():
    """Test WantedCriminalEvent with mid-range bounty."""
    with mock.patch("apps.city.events.events.wanted_criminal.random.randint") as mock_randint:
        mock_randint.return_value = 225

        event = WantedCriminalEvent()

        assert event.bounty == 225
