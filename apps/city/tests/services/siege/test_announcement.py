from unittest import mock

import pytest

from apps.city.constants import SIEGE_ADVANCE_ROUNDS, SIEGE_STRENGTH_MAX, SIEGE_STRENGTH_MIN
from apps.city.services.siege.announcement import SiegeAnnouncementService
from apps.savegame.models import PendingSiege
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_siege_announcement_service_roll_actual_strength():
    """Test _roll_actual_strength returns value within bounds."""
    savegame = SavegameFactory.create()
    service = SiegeAnnouncementService(savegame=savegame)

    with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
        mock_randint.return_value = 150
        result = service._roll_actual_strength()

    assert result == 150
    mock_randint.assert_called_once_with(SIEGE_STRENGTH_MIN, SIEGE_STRENGTH_MAX)


@pytest.mark.django_db
def test_siege_announcement_service_fuzz_strength_rounds_to_50():
    """Test _fuzz_strength rounds to nearest 50."""
    savegame = SavegameFactory.create()
    service = SiegeAnnouncementService(savegame=savegame)

    with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
        mock_uniform.return_value = 1.0
        result = service._fuzz_strength(actual=175)

    # 175 * 1.0 = 175, round to nearest 50 → 200
    assert result == 200
    assert result % 50 == 0


@pytest.mark.django_db
def test_siege_announcement_service_fuzz_strength_is_multiple_of_50():
    """Test _fuzz_strength always returns multiple of 50."""
    savegame = SavegameFactory.create()
    service = SiegeAnnouncementService(savegame=savegame)

    for fuzz in [0.75, 1.0, 1.25]:
        with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
            mock_uniform.return_value = fuzz
            result = service._fuzz_strength(actual=100)
        assert result % 50 == 0


@pytest.mark.django_db
def test_siege_announcement_service_pick_direction_no_walls():
    """Test _pick_direction picks randomly when no walls exist."""
    savegame = SavegameFactory.create()
    service = SiegeAnnouncementService(savegame=savegame)

    with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
        mock_choice.return_value = "N"
        result = service._pick_direction()

    assert result in ["N", "S", "E", "W"]
    mock_choice.assert_called_once()


@pytest.mark.django_db
def test_siege_announcement_service_pick_direction_weakest_segment():
    """Test _pick_direction picks the direction with lowest hp_ratio."""
    from apps.city.services.siege.segment import WallSegment

    savegame = SavegameFactory.create()
    service = SiegeAnnouncementService(savegame=savegame)

    mock_segments = {
        "N": WallSegment(direction="N", tiles=[], total_hp=0, total_max_hp=100, hp_ratio=0.0),
        "S": WallSegment(direction="S", tiles=[], total_hp=80, total_max_hp=100, hp_ratio=0.8),
        "E": WallSegment(direction="E", tiles=[], total_hp=60, total_max_hp=100, hp_ratio=0.6),
        "W": WallSegment(direction="W", tiles=[], total_hp=100, total_max_hp=100, hp_ratio=1.0),
    }

    with mock.patch("apps.city.services.siege.announcement.WallSegmentService") as mock_seg_svc:
        mock_seg_svc.return_value.process.return_value = mock_segments
        with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
            mock_choice.return_value = "N"
            result = service._pick_direction()

    # Only "N" has hp_ratio=0.0 (minimum)
    mock_choice.assert_called_once_with(["N"])
    assert result == "N"


@pytest.mark.django_db
def test_siege_announcement_service_pick_direction_tie():
    """Test _pick_direction picks randomly among tied weakest segments."""
    from apps.city.services.siege.segment import WallSegment

    savegame = SavegameFactory.create()
    service = SiegeAnnouncementService(savegame=savegame)

    mock_segments = {
        "N": WallSegment(direction="N", tiles=[], total_hp=0, total_max_hp=0, hp_ratio=0.0),
        "S": WallSegment(direction="S", tiles=[], total_hp=0, total_max_hp=0, hp_ratio=0.0),
        "E": WallSegment(direction="E", tiles=[], total_hp=0, total_max_hp=0, hp_ratio=0.0),
        "W": WallSegment(direction="W", tiles=[], total_hp=0, total_max_hp=0, hp_ratio=0.0),
    }

    with mock.patch("apps.city.services.siege.announcement.WallSegmentService") as mock_seg_svc:
        mock_seg_svc.return_value.process.return_value = mock_segments
        with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
            mock_choice.return_value = "S"
            service._pick_direction()

    # All tied, so all four should be passed to choice
    called_with = mock_choice.call_args[0][0]
    assert set(called_with) == {"N", "S", "E", "W"}


@pytest.mark.django_db
def test_siege_announcement_service_process_creates_pending_siege():
    """Test process() creates a PendingSiege record."""
    savegame = SavegameFactory.create(current_year=1150)

    with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
        mock_randint.return_value = 100
        with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
            mock_uniform.return_value = 1.0
            with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
                mock_choice.return_value = "N"
                siege = SiegeAnnouncementService(savegame=savegame).process()

    assert isinstance(siege, PendingSiege)
    assert siege.savegame == savegame
    assert siege.attack_year == 1150 + SIEGE_ADVANCE_ROUNDS
    assert siege.actual_strength == 100
    assert siege.announced_strength == 100  # 100 * 1.0 = 100, rounds to 100
    assert siege.direction == "N"
    assert siege.resolved is False


@pytest.mark.django_db
def test_siege_announcement_service_process_persists_to_db():
    """Test process() saves the PendingSiege to the database."""
    savegame = SavegameFactory.create(current_year=1150)

    with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
        mock_randint.return_value = 150
        with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
            mock_uniform.return_value = 1.0
            with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
                mock_choice.return_value = "S"
                SiegeAnnouncementService(savegame=savegame).process()

    assert savegame.pending_sieges.count() == 1
    siege = savegame.pending_sieges.first()
    assert siege.direction == "S"
