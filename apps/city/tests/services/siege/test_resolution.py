from unittest import mock

import pytest

from apps.city.services.siege.resolution import SiegeOutcome, SiegeResolutionService
from apps.city.services.siege.segment import WallSegment
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
    WallBuildingTypeFactory,
)
from apps.savegame.tests.factories import PendingSiegeFactory, SavegameFactory


def _make_wall_segment(*, tiles=None, total_hp=100, total_max_hp=100):
    tiles = tiles or []
    hp_ratio = total_hp / total_max_hp if total_max_hp > 0 else 0.0
    return WallSegment(direction="N", tiles=tiles, total_hp=total_hp, total_max_hp=total_max_hp, hp_ratio=hp_ratio)


@pytest.mark.django_db
def test_resolution_determine_outcome_repelled():
    """Test REPELLED when defense >= attack."""
    savegame = SavegameFactory.create()
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    result = service._determine_outcome(defense_score=100, attacker_strength=100)
    assert result == SiegeOutcome.Result.REPELLED

    result2 = service._determine_outcome(defense_score=200, attacker_strength=100)
    assert result2 == SiegeOutcome.Result.REPELLED


@pytest.mark.django_db
def test_resolution_determine_outcome_damaged():
    """Test DAMAGED when defense >= attack * 0.6 but < attack."""
    savegame = SavegameFactory.create()
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    # 60 >= 100*0.6=60 but < 100 → DAMAGED
    result = service._determine_outcome(defense_score=60, attacker_strength=100)
    assert result == SiegeOutcome.Result.DAMAGED

    result2 = service._determine_outcome(defense_score=80, attacker_strength=100)
    assert result2 == SiegeOutcome.Result.DAMAGED


@pytest.mark.django_db
def test_resolution_determine_outcome_breached():
    """Test BREACHED when defense < attack * 0.6."""
    savegame = SavegameFactory.create()
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    result = service._determine_outcome(defense_score=59, attacker_strength=100)
    assert result == SiegeOutcome.Result.BREACHED

    result2 = service._determine_outcome(defense_score=0, attacker_strength=100)
    assert result2 == SiegeOutcome.Result.BREACHED


@pytest.mark.django_db
def test_resolution_calculate_defense_score():
    """Test defense score is the segment's total_hp."""
    savegame = SavegameFactory.create()
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    segment = _make_wall_segment(total_hp=250)
    assert service._calculate_defense_score(segment=segment) == 250


@pytest.mark.django_db
def test_resolution_apply_repelled_returns_repelled_outcome(ruins_building):
    """Test _apply_repelled returns SiegeOutcome with REPELLED result."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=100)

    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=50, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)
    segment = _make_wall_segment(tiles=[tile], total_hp=100, total_max_hp=100)

    outcome = service._apply_repelled(segment=segment, defense_score=100)

    assert outcome.result == SiegeOutcome.Result.REPELLED
    assert outcome.direction == "N"
    assert outcome.attacker_strength == 50
    assert outcome.defense_score == 100
    assert outcome.buildings_damaged == 0
    assert outcome.population_lost == 0
    assert isinstance(outcome.report_text, str)
    assert len(outcome.report_text) > 0


@pytest.mark.django_db
def test_resolution_apply_repelled_damages_wall(ruins_building):
    """Test _apply_repelled damages some wall tiles."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=100)

    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=80, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)
    segment = _make_wall_segment(tiles=[tile], total_hp=100, total_max_hp=100)

    outcome = service._apply_repelled(segment=segment, defense_score=100)

    tile.refresh_from_db()
    assert tile.wall_hitpoints < 100
    assert outcome.wall_damage > 0


@pytest.mark.django_db
def test_resolution_apply_damaged_returns_damaged_outcome(ruins_building):
    """Test _apply_damaged returns SiegeOutcome with DAMAGED result."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=100)

    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)
    segment = _make_wall_segment(tiles=[tile], total_hp=100, total_max_hp=100)

    outcome = service._apply_damaged(segment=segment, defense_score=70)

    assert outcome.result == SiegeOutcome.Result.DAMAGED
    assert isinstance(outcome.report_text, str)


@pytest.mark.django_db
def test_resolution_apply_damaged_removes_building():
    """Test _apply_damaged removes 1 city building by calling RemoveBuilding."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wall_building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wall_building, wall_hitpoints=100)

    city_type = BuildingTypeFactory.create(is_city=True, is_wall=False, allowed_terrains=[terrain])
    city_building = BuildingFactory.create(building_type=city_type)
    TileFactory.create(savegame=savegame, x=10, y=10, terrain=terrain, building=city_building)

    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)
    segment = _make_wall_segment(tiles=[tile], total_hp=100, total_max_hp=100)

    with mock.patch("apps.city.services.siege.resolution.RemoveBuilding") as mock_rb:
        mock_rb.return_value.process.return_value = None
        outcome = service._apply_damaged(segment=segment, defense_score=70)

    assert outcome.buildings_damaged == 1
    mock_rb.assert_called_once()


@pytest.mark.django_db
def test_resolution_apply_breached_returns_breached_outcome(ruins_building):
    """Test _apply_breached returns SiegeOutcome with BREACHED result."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])

    tiles = []
    for y in range(5):
        wb = BuildingFactory.create(building_type=wall_type, level=1)
        t = TileFactory.create(savegame=savegame, x=y, y=2, terrain=terrain, building=wb, wall_hitpoints=100)
        tiles.append(t)

    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=200, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    # randint called 3 times: tiles_to_destroy_count, buildings_to_remove, population_lost
    with mock.patch("apps.city.services.siege.resolution.random.randint") as mock_randint:
        mock_randint.side_effect = [2, 1, 10]
        with mock.patch("apps.city.services.siege.resolution.random.sample") as mock_sample:
            mock_sample.return_value = tiles[:2]
            segment = _make_wall_segment(tiles=tiles, total_hp=500, total_max_hp=500)
            outcome = service._apply_breached(segment=segment, defense_score=20)

    assert outcome.result == SiegeOutcome.Result.BREACHED
    assert outcome.population_lost == 10
    assert outcome.wall_damage > 0


@pytest.mark.django_db
def test_resolution_apply_breached_destroys_wall_tiles(ruins_building):
    """Test _apply_breached sets wall tiles to ruins."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=100)

    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=200, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    # randint called 3 times: tiles_to_destroy_count, buildings_to_remove, population_lost
    with mock.patch("apps.city.services.siege.resolution.random.randint") as mock_randint:
        mock_randint.side_effect = [1, 1, 10]
        with mock.patch("apps.city.services.siege.resolution.random.sample") as mock_sample:
            mock_sample.return_value = [tile]
            segment = _make_wall_segment(tiles=[tile], total_hp=100, total_max_hp=100)
            service._apply_breached(segment=segment, defense_score=20)

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None


@pytest.mark.django_db
def test_resolution_process_repelled(ruins_building):
    """Test full process() for repelled scenario."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=200)

    # actual_strength=50, defense=200 → REPELLED
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=50, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)
    outcome = service.process()

    assert outcome.result == SiegeOutcome.Result.REPELLED


@pytest.mark.django_db
def test_resolution_process_damaged(ruins_building):
    """Test full process() for damaged scenario."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=70)

    # actual_strength=100, defense=70 → 70 >= 100*0.6=60 → DAMAGED
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)
    outcome = service.process()

    assert outcome.result == SiegeOutcome.Result.DAMAGED


@pytest.mark.django_db
def test_resolution_process_breached(ruins_building):
    """Test full process() for breached scenario."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=10)

    # actual_strength=300, defense=10 → 10 < 300*0.6=180 → BREACHED
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=300, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    # 3 randint calls: tiles_to_destroy_count, buildings_to_remove, population_lost
    with mock.patch("apps.city.services.siege.resolution.random.randint") as mock_randint:
        mock_randint.side_effect = [1, 1, 10]
        outcome = service.process()

    assert outcome.result == SiegeOutcome.Result.BREACHED


@pytest.mark.django_db
def test_resolution_process_no_walls_breached():
    """Test process() with no walls in segment → defense=0 → BREACHED."""
    savegame = SavegameFactory.create()
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    service = SiegeResolutionService(savegame=savegame, pending_siege=pending)

    # 3 randint calls: tiles_to_destroy_count, buildings_to_remove, population_lost
    with mock.patch("apps.city.services.siege.resolution.random.randint") as mock_randint:
        mock_randint.side_effect = [1, 1, 10]
        outcome = service.process()

    assert outcome.result == SiegeOutcome.Result.BREACHED
    assert outcome.wall_damage == 0
