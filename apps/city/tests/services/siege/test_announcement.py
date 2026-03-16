from unittest import mock

import pytest

from apps.city.constants import SIEGE_ADVANCE_ROUNDS, SIEGE_STRENGTH_MAX, SIEGE_STRENGTH_MIN
from apps.city.services.siege.announcement import SiegeAnnouncementService
from apps.city.tests.factories import BuildingFactory, TerrainFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.models import PendingSiege
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_siege_announcement_service_process_creates_pending_siege():
    """Test process() creates a PendingSiege record with correct values."""
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
    assert siege.direction == "N"
    assert siege.resolved is False
    mock_randint.assert_called_once_with(SIEGE_STRENGTH_MIN, SIEGE_STRENGTH_MAX)


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


@pytest.mark.django_db
def test_siege_announcement_service_process_announced_strength_rounds_to_50():
    """Test that announced_strength is rounded to the nearest 50."""
    savegame = SavegameFactory.create(current_year=1150)

    with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
        mock_randint.return_value = 175
        with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
            mock_uniform.return_value = 1.0
            with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
                mock_choice.return_value = "N"
                siege = SiegeAnnouncementService(savegame=savegame).process()

    # 175 * 1.0 = 175, rounds to nearest 50 → 200
    assert siege.announced_strength == 200
    assert siege.announced_strength % 50 == 0


@pytest.mark.django_db
def test_siege_announcement_service_process_announced_strength_is_always_multiple_of_50():
    """Test announced_strength is always a multiple of 50 regardless of fuzz factor."""
    savegame = SavegameFactory.create(current_year=1150)

    for fuzz in [0.75, 1.0, 1.25]:
        with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
            mock_randint.return_value = 100
            with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
                mock_uniform.return_value = fuzz
                with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
                    mock_choice.return_value = "N"
                    siege = SiegeAnnouncementService(savegame=savegame).process()

        assert siege.announced_strength % 50 == 0


@pytest.mark.django_db
def test_siege_announcement_service_process_picks_weakest_direction():
    """Test process() picks the wall segment with the lowest HP ratio as target direction."""
    savegame = SavegameFactory.create(current_year=1150)
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])

    # N, S, W walls: full HP (100/100) → ratio=1.0
    for x, y in [(9, 2), (9, 18), (1, 10)]:
        wb = BuildingFactory.create(building_type=wall_type, level=1)
        TileFactory.create(savegame=savegame, x=x, y=y, terrain=terrain, building=wb, wall_hitpoints=100)

    # E wall: x=18, y=10 → clearly East — damaged (10/100) → ratio=0.1, uniquely weakest
    wb_e = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, x=18, y=10, terrain=terrain, building=wb_e, wall_hitpoints=10)

    with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
        mock_randint.return_value = 100
        with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
            mock_uniform.return_value = 1.0
            siege = SiegeAnnouncementService(savegame=savegame).process()

    assert siege.direction == "E"


@pytest.mark.django_db
def test_siege_announcement_service_process_picks_randomly_when_directions_tied():
    """Test process() picks randomly among tied weakest segments."""
    savegame = SavegameFactory.create(current_year=1150)

    # No wall tiles → all segments have hp_ratio=0.0, a tie across all four
    with mock.patch("apps.city.services.siege.announcement.random.randint") as mock_randint:
        mock_randint.return_value = 100
        with mock.patch("apps.city.services.siege.announcement.random.uniform") as mock_uniform:
            mock_uniform.return_value = 1.0
            with mock.patch("apps.city.services.siege.announcement.random.choice") as mock_choice:
                mock_choice.return_value = "S"
                SiegeAnnouncementService(savegame=savegame).process()

    called_with = mock_choice.call_args[0][0]
    assert set(called_with) == {"N", "S", "E", "W"}
