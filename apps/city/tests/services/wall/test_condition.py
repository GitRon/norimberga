import pytest

from apps.city.services.wall.condition import WallConditionService
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_wall_condition_service_returns_wall_tiles():
    """Test service returns all wall tiles for the savegame."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile1 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)
    tile2 = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=80)

    result = WallConditionService(savegame=savegame).process()

    tile_ids = {t.id for t in result.tiles}
    assert tile1.id in tile_ids
    assert tile2.id in tile_ids


@pytest.mark.django_db
def test_wall_condition_service_aggregates_hp():
    """Test service correctly sums total_hp and total_max_hp."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=80)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=60)

    result = WallConditionService(savegame=savegame).process()

    assert result.total_hp == 140
    assert result.total_max_hp == 200


@pytest.mark.django_db
def test_wall_condition_service_health_percent():
    """Test service computes health_percent correctly."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=50)

    result = WallConditionService(savegame=savegame).process()

    assert result.health_percent == 50


@pytest.mark.django_db
def test_wall_condition_service_no_walls():
    """Test service returns zero values when no wall tiles exist."""
    savegame = SavegameFactory.create()

    result = WallConditionService(savegame=savegame).process()

    assert result.tiles == []
    assert result.total_hp == 0
    assert result.total_max_hp == 0
    assert result.health_percent == 0


@pytest.mark.django_db
def test_wall_condition_service_skips_tiles_without_hitpoints():
    """Test service excludes tiles where wall_hitpoints is None from the hp total, but includes their max_hp."""
    savegame = SavegameFactory.create()
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    TileFactory.create(savegame=savegame, building=building, wall_hitpoints=None)

    result = WallConditionService(savegame=savegame).process()

    assert len(result.tiles) == 1
    assert result.total_hp == 0
    assert result.total_max_hp == 100  # max_hp is still known from building level
    assert result.health_percent == 0
