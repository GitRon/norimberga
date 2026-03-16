from unittest import mock

import pytest

from apps.city.services.siege.resolution import SiegeOutcome, SiegeResolutionService
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
    WallBuildingTypeFactory,
)
from apps.savegame.tests.factories import PendingSiegeFactory, SavegameFactory


@pytest.mark.django_db
def test_resolution_process_repelled(ruins_building):
    """Test full process() for repelled scenario: defense >= attack."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=200)

    # actual_strength=50, defense=200 → REPELLED
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=50, direction="N")
    outcome = SiegeResolutionService(savegame=savegame, pending_siege=pending).process()

    assert outcome.result == SiegeOutcome.Result.REPELLED
    assert outcome.direction == "N"
    assert outcome.attacker_strength == 50
    assert outcome.defense_score == 200
    assert outcome.buildings_damaged == 0
    assert outcome.population_lost == 0
    assert len(outcome.report_text) > 0

    tile.refresh_from_db()
    assert tile.wall_hitpoints < 200


@pytest.mark.django_db
def test_resolution_process_damaged(ruins_building):
    """Test full process() for damaged scenario: defense >= attack * 0.6 but < attack."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=70)

    city_type = BuildingTypeFactory.create(is_city=True, is_wall=False, allowed_terrains=[terrain])
    city_building = BuildingFactory.create(building_type=city_type)
    city_tile = TileFactory.create(savegame=savegame, x=10, y=10, terrain=terrain, building=city_building)

    # actual_strength=100, defense=70 → 70 >= 100*0.6=60 → DAMAGED
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")
    outcome = SiegeResolutionService(savegame=savegame, pending_siege=pending).process()

    assert outcome.result == SiegeOutcome.Result.DAMAGED
    assert outcome.buildings_damaged == 1
    assert outcome.population_lost == 0
    assert len(outcome.report_text) > 0

    tile.refresh_from_db()
    assert tile.wall_hitpoints < 70

    city_tile.refresh_from_db()
    assert city_tile.building == ruins_building


@pytest.mark.django_db
def test_resolution_process_breached(ruins_building):
    """Test full process() for breached scenario: defense < attack * 0.6."""
    savegame = SavegameFactory.create()
    terrain = TerrainFactory.create()
    wall_type = WallBuildingTypeFactory.create(allowed_terrains=[terrain])
    wb = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, x=9, y=2, terrain=terrain, building=wb, wall_hitpoints=10)

    # actual_strength=300, defense=10 → 10 < 300*0.6=180 → BREACHED
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=300, direction="N")

    # 3 randint calls: tiles_to_destroy_count, buildings_to_remove, population_lost
    with mock.patch("apps.city.services.siege.resolution.random.randint") as mock_randint:
        mock_randint.side_effect = [1, 1, 10]
        outcome = SiegeResolutionService(savegame=savegame, pending_siege=pending).process()

    assert outcome.result == SiegeOutcome.Result.BREACHED
    assert outcome.population_lost == 10
    assert outcome.wall_damage > 0
    assert len(outcome.report_text) > 0

    tile.refresh_from_db()
    assert tile.wall_hitpoints is None


@pytest.mark.django_db
def test_resolution_process_no_walls_breached():
    """Test process() with no walls in segment → defense=0 → BREACHED."""
    savegame = SavegameFactory.create()
    pending = PendingSiegeFactory.create(savegame=savegame, actual_strength=100, direction="N")

    # 3 randint calls: tiles_to_destroy_count, buildings_to_remove, population_lost
    with mock.patch("apps.city.services.siege.resolution.random.randint") as mock_randint:
        mock_randint.side_effect = [1, 1, 10]
        outcome = SiegeResolutionService(savegame=savegame, pending_siege=pending).process()

    assert outcome.result == SiegeOutcome.Result.BREACHED
    assert outcome.wall_damage == 0
