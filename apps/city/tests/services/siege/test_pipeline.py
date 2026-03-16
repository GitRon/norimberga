from unittest import mock

import pytest

from apps.city.services.siege.pipeline import SiegePipelineService
from apps.city.services.siege.resolution import SiegeOutcome
from apps.savegame.models import SiegeChronicle
from apps.savegame.tests.factories import PendingSiegeFactory, SavegameFactory


@pytest.mark.django_db
def test_siege_pipeline_no_due_siege():
    """Test process() returns None when no siege is due."""
    savegame = SavegameFactory.create(current_year=1155)
    result = SiegePipelineService(savegame=savegame).process()
    assert result is None


@pytest.mark.django_db
def test_siege_pipeline_no_due_siege_already_resolved():
    """Test process() returns None when pending siege is resolved."""
    savegame = SavegameFactory.create(current_year=1155)
    PendingSiegeFactory.create(savegame=savegame, attack_year=1155, resolved=True)

    result = SiegePipelineService(savegame=savegame).process()
    assert result is None


@pytest.mark.django_db
def test_siege_pipeline_no_due_siege_wrong_year():
    """Test process() returns None when siege is for a different year."""
    savegame = SavegameFactory.create(current_year=1155)
    PendingSiegeFactory.create(savegame=savegame, attack_year=1160, resolved=False)

    result = SiegePipelineService(savegame=savegame).process()
    assert result is None


@pytest.mark.django_db
def test_siege_pipeline_resolves_due_siege(ruins_building):
    """Test process() resolves a due siege and returns outcome."""
    savegame = SavegameFactory.create(current_year=1155)
    PendingSiegeFactory.create(savegame=savegame, attack_year=1155, resolved=False, actual_strength=50, direction="N")

    mock_outcome = SiegeOutcome(
        result=SiegeOutcome.Result.REPELLED,
        direction="N",
        attacker_strength=50,
        defense_score=200,
        wall_damage=5,
        buildings_damaged=0,
        population_lost=0,
        report_text="Enemy repelled.",
    )

    with mock.patch("apps.city.services.siege.pipeline.SiegeResolutionService") as mock_resolution:
        mock_resolution.return_value.process.return_value = mock_outcome
        result = SiegePipelineService(savegame=savegame).process()

    assert result == mock_outcome


@pytest.mark.django_db
def test_siege_pipeline_marks_siege_resolved(ruins_building):
    """Test process() marks the pending siege as resolved."""
    savegame = SavegameFactory.create(current_year=1155)
    pending = PendingSiegeFactory.create(
        savegame=savegame, attack_year=1155, resolved=False, actual_strength=50, direction="N"
    )

    mock_outcome = SiegeOutcome(
        result=SiegeOutcome.Result.REPELLED,
        direction="N",
        attacker_strength=50,
        defense_score=200,
        wall_damage=0,
        buildings_damaged=0,
        population_lost=0,
        report_text="Enemy repelled.",
    )

    with mock.patch("apps.city.services.siege.pipeline.SiegeResolutionService") as mock_resolution:
        mock_resolution.return_value.process.return_value = mock_outcome
        SiegePipelineService(savegame=savegame).process()

    pending.refresh_from_db()
    assert pending.resolved is True


@pytest.mark.django_db
def test_siege_pipeline_creates_chronicle(ruins_building):
    """Test process() creates a SiegeChronicle record."""
    savegame = SavegameFactory.create(current_year=1155)
    PendingSiegeFactory.create(savegame=savegame, attack_year=1155, resolved=False, actual_strength=100, direction="S")

    mock_outcome = SiegeOutcome(
        result=SiegeOutcome.Result.DAMAGED,
        direction="S",
        attacker_strength=100,
        defense_score=70,
        wall_damage=40,
        buildings_damaged=1,
        population_lost=0,
        report_text="South wall damaged.",
    )

    with mock.patch("apps.city.services.siege.pipeline.SiegeResolutionService") as mock_resolution:
        mock_resolution.return_value.process.return_value = mock_outcome
        SiegePipelineService(savegame=savegame).process()

    assert savegame.siege_chronicles.count() == 1
    chronicle = savegame.siege_chronicles.first()
    assert chronicle.year == 1155
    assert chronicle.direction == "S"
    assert chronicle.attacker_strength == 100
    assert chronicle.defense_score == 70
    assert chronicle.result == SiegeChronicle.Result.DAMAGED
    assert chronicle.report_text == "South wall damaged."


@pytest.mark.django_db
def test_siege_pipeline_creates_notification(ruins_building):
    """Test process() creates an EventNotification for the player."""
    savegame = SavegameFactory.create(current_year=1155)
    PendingSiegeFactory.create(savegame=savegame, attack_year=1155, resolved=False, actual_strength=100, direction="N")

    mock_outcome = SiegeOutcome(
        result=SiegeOutcome.Result.REPELLED,
        direction="N",
        attacker_strength=100,
        defense_score=200,
        wall_damage=10,
        buildings_damaged=0,
        population_lost=0,
        report_text="Enemy repelled at the North wall.",
    )

    with mock.patch("apps.city.services.siege.pipeline.SiegeResolutionService") as mock_resolution:
        mock_resolution.return_value.process.return_value = mock_outcome
        SiegePipelineService(savegame=savegame).process()

    notifications = savegame.event_notifications.filter(acknowledged=False)
    assert notifications.count() == 1
    notification = notifications.first()
    assert "Battle Report" in notification.title
    assert notification.message == "Enemy repelled at the North wall."
    assert notification.year == 1155


@pytest.mark.django_db
def test_siege_pipeline_notification_title_for_breached(ruins_building):
    """Test notification title reflects breach outcome."""
    savegame = SavegameFactory.create(current_year=1155)
    PendingSiegeFactory.create(savegame=savegame, attack_year=1155, resolved=False, actual_strength=300, direction="N")

    mock_outcome = SiegeOutcome(
        result=SiegeOutcome.Result.BREACHED,
        direction="N",
        attacker_strength=300,
        defense_score=10,
        wall_damage=100,
        buildings_damaged=2,
        population_lost=15,
        report_text="Wall breached!",
    )

    with mock.patch("apps.city.services.siege.pipeline.SiegeResolutionService") as mock_resolution:
        mock_resolution.return_value.process.return_value = mock_outcome
        SiegePipelineService(savegame=savegame).process()

    notification = savegame.event_notifications.first()
    assert "Breached" in notification.title
