import pytest
from django.contrib import messages

from apps.city.events.events.rain_procession import Event as RainProcessionEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_rain_procession_event_init():
    """Test RainProcessionEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    event = RainProcessionEvent(savegame=savegame)

    assert event.PROBABILITY == 15
    assert event.LEVEL == messages.INFO
    assert event.TITLE == "Rain Procession"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_rain_procession_event_get_probability_with_population():
    """Test get_probability returns base probability when population > 0."""
    savegame = SavegameFactory(population=50)

    event = RainProcessionEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 15


@pytest.mark.django_db
def test_rain_procession_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)

    event = RainProcessionEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_rain_procession_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=100)

    event = RainProcessionEvent(savegame=savegame)
    verbose_text = event.get_verbose_text()

    expected_text = "A priest organizes a rain prayer; it immediately starts raining inside the church instead."
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_rain_procession_event_get_effects():
    """Test get_effects returns empty list."""
    savegame = SavegameFactory(population=100)

    event = RainProcessionEvent(savegame=savegame)
    effects = event.get_effects()

    assert len(effects) == 0


@pytest.mark.django_db
def test_rain_procession_event_process():
    """Test full event processing workflow."""
    savegame = SavegameFactory(population=100)

    event = RainProcessionEvent(savegame=savegame)
    result_text = event.process()

    # Verify no changes to savegame
    savegame.refresh_from_db()
    assert savegame.population == 100

    # Verify result text is returned
    assert "A priest organizes a rain prayer" in result_text
    assert "raining inside the church" in result_text
