from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.events.events.good_harvest import Event as GoodHarvestEvent
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_good_harvest_event_init():
    """Test GoodHarvestEvent initialization and class attributes."""
    savegame = SavegameFactory(unrest=30)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 5

        event = GoodHarvestEvent(savegame=savegame)

        assert event.PROBABILITY == 13
        assert event.LEVEL == messages.SUCCESS
        assert event.TITLE == "Good Harvest"
        assert event.savegame.id == savegame.id
        assert event.initial_unrest == 30
        assert event.lost_unrest == 5


@pytest.mark.django_db
def test_good_harvest_event_init_creates_savegame():
    """Test GoodHarvestEvent creates savegame if it doesn't exist."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 3

        event = GoodHarvestEvent(savegame=savegame)

        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_good_harvest_event_get_probability_with_conditions():
    """Test get_probability returns base probability when conditions are met."""
    savegame = SavegameFactory(unrest=20, population=50)

    event = GoodHarvestEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 13


@pytest.mark.django_db
def test_good_harvest_event_get_probability_zero_unrest():
    """Test get_probability returns 0 when unrest is zero."""
    savegame = SavegameFactory(unrest=0, population=50)

    event = GoodHarvestEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_good_harvest_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(unrest=30, population=0)

    event = GoodHarvestEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_good_harvest_event_get_probability_both_zero():
    """Test get_probability returns 0 when both unrest and population are zero."""
    savegame = SavegameFactory(unrest=0, population=0)

    event = GoodHarvestEvent(savegame=savegame)

    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_good_harvest_event_prepare_effect_decrease_unrest():
    """Test _prepare_effect_decrease_unrest returns correct effect."""
    savegame = SavegameFactory(unrest=25)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 7

        event = GoodHarvestEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_unrest()

        assert isinstance(effect, DecreaseUnrestAbsolute)
        assert effect.lost_unrest == 7


@pytest.mark.django_db
def test_good_harvest_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(unrest=40)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 6

        event = GoodHarvestEvent(savegame=savegame)
        initial_unrest = event.initial_unrest

        # Simulate effect processing (decrease unrest)
        savegame.unrest = max(savegame.unrest - 6, 0)
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            f"A good harvest reduces food prices, bringing relief to the population. "
            f"The unrest drops by {initial_unrest - savegame.unrest}%."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_good_harvest_event_process():
    """Test full event processing workflow."""
    savegame = SavegameFactory(unrest=30, population=100)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 8

        event = GoodHarvestEvent(savegame=savegame)
        result_text = event.process()

        # Verify effect was applied
        savegame.refresh_from_db()
        assert savegame.unrest == 22  # 30 - 8 = 22

        # Verify result text is returned
        assert "A good harvest reduces food prices, bringing relief to the population" in result_text
        assert "The unrest drops by 8%" in result_text


@pytest.mark.django_db
def test_good_harvest_event_get_effects():
    """Test get_effects returns list of effects."""
    savegame = SavegameFactory(unrest=20)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 4

        event = GoodHarvestEvent(savegame=savegame)
        effects = event.get_effects()

        assert len(effects) == 1
        assert isinstance(effects[0], DecreaseUnrestAbsolute)
        assert effects[0].lost_unrest == 4


@pytest.mark.django_db
def test_good_harvest_event_random_range_minimum():
    """Test event with minimum random unrest reduction."""
    savegame = SavegameFactory(unrest=50)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 1

        event = GoodHarvestEvent(savegame=savegame)

        assert event.lost_unrest == 1


@pytest.mark.django_db
def test_good_harvest_event_random_range_maximum():
    """Test event with maximum random unrest reduction."""
    savegame = SavegameFactory(unrest=50)

    with mock.patch("apps.city.events.events.good_harvest.random.randint") as mock_randint:
        mock_randint.return_value = 10

        event = GoodHarvestEvent(savegame=savegame)

        assert event.lost_unrest == 10
