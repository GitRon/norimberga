import pytest
from django.contrib import messages

from apps.city.events.events.lost_hour import Event as LostHourEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_lost_hour_event_init():
    """Test LostHourEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    event = LostHourEvent(savegame=savegame)

    assert event.PROBABILITY == 15
    assert event.LEVEL == messages.INFO
    assert event.TITLE == "Lost Hour"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_lost_hour_event_get_probability_with_population():
    """Test get_probability returns base probability when population > 0."""
    savegame = SavegameFactory(population=50)

    event = LostHourEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 15


@pytest.mark.django_db
def test_lost_hour_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)

    event = LostHourEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_lost_hour_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=100)

    event = LostHourEvent(savegame=savegame)
    verbose_text = event.get_verbose_text()

    expected_text = (
        "A group of townsfolk insists the bell tower rang thirteen times last night. The bell ringer denies everything."
    )
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_lost_hour_event_get_effects():
    """Test get_effects returns empty list."""
    savegame = SavegameFactory(population=100)

    event = LostHourEvent(savegame=savegame)
    effects = event.get_effects()

    assert len(effects) == 0


@pytest.mark.django_db
def test_lost_hour_event_process():
    """Test full event processing workflow."""
    savegame = SavegameFactory(population=100)

    event = LostHourEvent(savegame=savegame)
    result_text = event.process()

    # Verify no changes to savegame
    savegame.refresh_from_db()
    assert savegame.population == 100

    # Verify result text is returned
    assert "the bell tower rang thirteen times last night" in result_text
    assert "The bell ringer denies everything" in result_text
