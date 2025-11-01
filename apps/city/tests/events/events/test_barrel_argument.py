import pytest
from django.contrib import messages

from apps.city.events.events.barrel_argument import Event as BarrelArgumentEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_barrel_argument_event_init():
    """Test BarrelArgumentEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    event = BarrelArgumentEvent(savegame=savegame)

    assert event.PROBABILITY == 1
    assert event.LEVEL == messages.INFO
    assert event.TITLE == "The Barrel Argument"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_barrel_argument_event_get_probability_with_population():
    """Test get_probability returns base probability when population > 0."""
    savegame = SavegameFactory(population=50)

    event = BarrelArgumentEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 1


@pytest.mark.django_db
def test_barrel_argument_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)

    event = BarrelArgumentEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_barrel_argument_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=100)

    event = BarrelArgumentEvent(savegame=savegame)
    verbose_text = event.get_verbose_text()

    expected_text = (
        'Two brewers are loudly debating in the square about which barrel of ale is "properly blessed." '
        "The local priest looks deeply uncomfortable."
    )
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_barrel_argument_event_get_effects():
    """Test get_effects returns empty list."""
    savegame = SavegameFactory(population=100)

    event = BarrelArgumentEvent(savegame=savegame)
    effects = event.get_effects()

    assert len(effects) == 0


@pytest.mark.django_db
def test_barrel_argument_event_process():
    """Test full event processing workflow."""
    savegame = SavegameFactory(population=100)

    event = BarrelArgumentEvent(savegame=savegame)
    result_text = event.process()

    # Verify no changes to savegame
    savegame.refresh_from_db()
    assert savegame.population == 100

    # Verify result text is returned
    assert "Two brewers are loudly debating in the square" in result_text
    assert "properly blessed" in result_text
