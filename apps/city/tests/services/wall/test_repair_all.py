import pytest

from apps.city.services.wall.repair_all import WallRepairAllService
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_process_repairs_all_damaged_walls():
    savegame = SavegameFactory(coins=500)
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(savegame=savegame, building=building, wall_hitpoints=50)

    WallRepairAllService(savegame=savegame).process()

    tile.refresh_from_db()
    assert tile.wall_hitpoints == 100


@pytest.mark.django_db
def test_process_deducts_correct_coins():
    savegame = SavegameFactory(coins=500)
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    TileFactory(savegame=savegame, building=building, wall_hitpoints=50)

    WallRepairAllService(savegame=savegame).process()

    savegame.refresh_from_db()
    assert savegame.coins == 450


@pytest.mark.django_db
def test_process_repairs_multiple_tiles():
    savegame = SavegameFactory(coins=500)
    wall_building_type = WallBuildingTypeFactory()
    building_a = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    building_b = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile_a = TileFactory(savegame=savegame, building=building_a, wall_hitpoints=0)
    tile_b = TileFactory(savegame=savegame, building=building_b, wall_hitpoints=0)

    WallRepairAllService(savegame=savegame).process()

    tile_a.refresh_from_db()
    tile_b.refresh_from_db()
    assert tile_a.wall_hitpoints == 100
    assert tile_b.wall_hitpoints == 100


@pytest.mark.django_db
def test_process_raises_when_not_enough_coins():
    savegame = SavegameFactory(coins=10)
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    TileFactory(savegame=savegame, building=building, wall_hitpoints=0)

    with pytest.raises(ValueError, match="Not enough coins"):
        WallRepairAllService(savegame=savegame).process()


@pytest.mark.django_db
def test_process_does_nothing_when_no_damaged_walls():
    savegame = SavegameFactory(coins=500)
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(savegame=savegame, building=building, wall_hitpoints=100)

    WallRepairAllService(savegame=savegame).process()

    savegame.refresh_from_db()
    tile.refresh_from_db()
    assert savegame.coins == 500
    assert tile.wall_hitpoints == 100
