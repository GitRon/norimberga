from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.events.siege_warning import Event as SiegeWarningEvent
from apps.savegame.tests.factories import PendingSiegeFactory, SavegameFactory


@pytest.mark.django_db
def test_siege_warning_event_probability():
    """Test PROBABILITY is 8."""
    assert SiegeWarningEvent.PROBABILITY == 8


@pytest.mark.django_db
def test_siege_warning_event_level():
    """Test LEVEL is WARNING."""
    assert SiegeWarningEvent.LEVEL == messages.WARNING


@pytest.mark.django_db
def test_siege_warning_event_title():
    """Test TITLE contains scout report."""
    assert "Scout" in SiegeWarningEvent.TITLE


@pytest.mark.django_db
def test_siege_warning_event_get_probability_no_pending_siege():
    """Test get_probability returns base probability when no siege is pending."""
    savegame = SavegameFactory.create()
    event = SiegeWarningEvent(savegame=savegame)

    assert event.get_probability() == 8


@pytest.mark.django_db
def test_siege_warning_event_get_probability_with_pending_siege():
    """Test get_probability returns 0 when a siege is already pending."""
    savegame = SavegameFactory.create()
    PendingSiegeFactory.create(savegame=savegame, resolved=False)
    event = SiegeWarningEvent(savegame=savegame)

    assert event.get_probability() == 0


@pytest.mark.django_db
def test_siege_warning_event_get_probability_resolved_siege_allows_new():
    """Test get_probability returns base probability when only resolved sieges exist."""
    savegame = SavegameFactory.create()
    PendingSiegeFactory.create(savegame=savegame, resolved=True)
    event = SiegeWarningEvent(savegame=savegame)

    assert event.get_probability() == 8


@pytest.mark.django_db
def test_siege_warning_event_get_effects_returns_empty():
    """Test get_effects returns empty list."""
    savegame = SavegameFactory.create()
    event = SiegeWarningEvent(savegame=savegame)

    assert event.get_effects() == []


@pytest.mark.django_db
def test_siege_warning_event_process_creates_pending_siege():
    """Test process() creates a PendingSiege record."""
    savegame = SavegameFactory.create(current_year=1150)

    mock_siege = PendingSiegeFactory.build(
        savegame=savegame,
        attack_year=1153,
        announced_strength=150,
        direction="N",
    )
    mock_siege.pk = 1  # Simulate saved state

    with mock.patch("apps.city.events.events.siege_warning.SiegeAnnouncementService") as mock_svc:
        mock_svc.return_value.process.return_value = mock_siege
        event = SiegeWarningEvent(savegame=savegame)
        event.process()

    mock_svc.assert_called_once_with(savegame=savegame)
    mock_svc.return_value.process.assert_called_once()


@pytest.mark.django_db
def test_siege_warning_event_process_returns_verbose_text():
    """Test process() returns a non-empty string."""
    savegame = SavegameFactory.create(current_year=1150)

    mock_siege = PendingSiegeFactory.build(
        savegame=savegame,
        attack_year=1153,
        announced_strength=150,
        direction="N",
    )
    mock_siege.pk = 1

    with mock.patch("apps.city.events.events.siege_warning.SiegeAnnouncementService") as mock_svc:
        mock_svc.return_value.process.return_value = mock_siege
        event = SiegeWarningEvent(savegame=savegame)
        result = event.process()

    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.django_db
def test_siege_warning_event_get_verbose_text_contains_direction():
    """Test get_verbose_text includes direction name."""
    savegame = SavegameFactory.create(current_year=1150)

    for direction, name in [("N", "North"), ("S", "South"), ("E", "East"), ("W", "West")]:
        mock_siege = PendingSiegeFactory.build(
            savegame=savegame,
            attack_year=1153,
            announced_strength=200,
            direction=direction,
        )
        mock_siege.pk = 1

        with mock.patch("apps.city.events.events.siege_warning.SiegeAnnouncementService") as mock_svc:
            mock_svc.return_value.process.return_value = mock_siege
            event = SiegeWarningEvent(savegame=savegame)
            event._pending_siege = mock_siege
            text = event.get_verbose_text()

        assert name in text


@pytest.mark.django_db
def test_siege_warning_event_get_verbose_text_contains_strength():
    """Test get_verbose_text includes announced strength."""
    savegame = SavegameFactory.create(current_year=1150)

    mock_siege = PendingSiegeFactory.build(
        savegame=savegame,
        attack_year=1153,
        announced_strength=250,
        direction="E",
    )
    mock_siege.pk = 1

    with mock.patch("apps.city.events.events.siege_warning.SiegeAnnouncementService") as mock_svc:
        mock_svc.return_value.process.return_value = mock_siege
        event = SiegeWarningEvent(savegame=savegame)
        event._pending_siege = mock_siege
        text = event.get_verbose_text()

    assert "250" in text


@pytest.mark.django_db
def test_siege_warning_event_get_verbose_text_contains_years_away():
    """Test get_verbose_text mentions number of years until attack."""
    savegame = SavegameFactory.create(current_year=1150)

    mock_siege = PendingSiegeFactory.build(
        savegame=savegame,
        attack_year=1153,
        announced_strength=100,
        direction="N",
    )
    mock_siege.pk = 1

    with mock.patch("apps.city.events.events.siege_warning.SiegeAnnouncementService") as mock_svc:
        mock_svc.return_value.process.return_value = mock_siege
        event = SiegeWarningEvent(savegame=savegame)
        event._pending_siege = mock_siege
        text = event.get_verbose_text()

    assert "3" in text
