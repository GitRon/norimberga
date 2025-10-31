import pytest
from django.contrib import messages

from apps.city.events.events.overpriced_turnip import Event as OverpricedTurnipEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_overpriced_turnip_event_init():
    """Test OverpricedTurnipEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100)

    event = OverpricedTurnipEvent(savegame=savegame)

    assert event.PROBABILITY == 15
    assert event.LEVEL == messages.INFO
    assert event.TITLE == "Overpriced Turnip"
    assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_overpriced_turnip_event_get_probability_with_population():
    """Test get_probability returns base probability when population > 0."""
    savegame = SavegameFactory(population=50)

    event = OverpricedTurnipEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 15


@pytest.mark.django_db
def test_overpriced_turnip_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0)

    event = OverpricedTurnipEvent(savegame=savegame)
    probability = event.get_probability()

    assert probability == 0


@pytest.mark.django_db
def test_overpriced_turnip_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=100)

    event = OverpricedTurnipEvent(savegame=savegame)
    verbose_text = event.get_verbose_text()

    expected_text = "A merchant swears his turnips are magical. A few gullible townsfolk buy them just in case."
    assert verbose_text == expected_text


@pytest.mark.django_db
def test_overpriced_turnip_event_get_effects():
    """Test get_effects returns empty list."""
    savegame = SavegameFactory(population=100)

    event = OverpricedTurnipEvent(savegame=savegame)
    effects = event.get_effects()

    assert len(effects) == 0


@pytest.mark.django_db
def test_overpriced_turnip_event_process():
    """Test full event processing workflow."""
    savegame = SavegameFactory(population=100)

    event = OverpricedTurnipEvent(savegame=savegame)
    result_text = event.process()

    # Verify no changes to savegame
    savegame.refresh_from_db()
    assert savegame.population == 100

    # Verify result text is returned
    assert "A merchant swears his turnips are magical" in result_text
    assert "gullible townsfolk" in result_text
