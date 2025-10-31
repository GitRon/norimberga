import pytest
from django.contrib import messages

from apps.city.events.events.unexpected_bard import Event as UnexpectedBardEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_unexpected_bard_event_init():
    """Test UnexpectedBardEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    event = UnexpectedBardEvent(savegame=savegame)

    assert event.PROBABILITY == 15
    assert event.LEVEL == messages.INFO
    assert event.TITLE == "Unexpected Bard"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_unexpected_bard_event_get_probability_with_population():
    """Test get_probability returns base probability when population > 0."""
    savegame = SavegameFactory(population=50)

    event = UnexpectedBardEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 15


@pytest.mark.django_db
def test_unexpected_bard_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)

    event = UnexpectedBardEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_unexpected_bard_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=100)

    event = UnexpectedBardEvent(savegame=savegame)
    verbose_text = event.get_verbose_text()

    expected_text = (
        'A bard writes songs about "everyday heroes" — '
        "like the cooper's assistant or the laundress with strong arms. "
        "It's awkwardly specific."
    )
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_unexpected_bard_event_get_effects():
    """Test get_effects returns empty list."""
    savegame = SavegameFactory(population=100)

    event = UnexpectedBardEvent(savegame=savegame)
    effects = event.get_effects()

    assert len(effects) == 0


@pytest.mark.django_db
def test_unexpected_bard_event_process():
    """Test full event processing workflow."""
    savegame = SavegameFactory(population=100)

    event = UnexpectedBardEvent(savegame=savegame)
    result_text = event.process()

    # Verify no changes to savegame
    savegame.refresh_from_db()
    assert savegame.population == 100

    # Verify result text is returned
    assert "A bard writes songs about" in result_text
    assert "everyday heroes" in result_text
