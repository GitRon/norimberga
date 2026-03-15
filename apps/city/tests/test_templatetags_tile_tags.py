from apps.city.templatetags.tile_tags import wall_hp_percent
from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory


def test_wall_hp_percent_returns_100_when_full_health(db):
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1)
    tile = TileFactory(building=building, wall_hitpoints=100)

    assert wall_hp_percent(tile) == 100


def test_wall_hp_percent_returns_50_when_half_health(db):
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1)
    tile = TileFactory(building=building, wall_hitpoints=50)

    assert wall_hp_percent(tile) == 50


def test_wall_hp_percent_returns_0_when_no_health(db):
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1)
    tile = TileFactory(building=building, wall_hitpoints=0)

    assert wall_hp_percent(tile) == 0


def test_wall_hp_percent_returns_none_for_non_wall_tile(db):
    tile = TileFactory(building=None, wall_hitpoints=None)

    assert wall_hp_percent(tile) is None


def test_wall_hp_percent_returns_none_when_wall_hitpoints_is_none(db):
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1)
    tile = TileFactory(building=building, wall_hitpoints=None)

    assert wall_hp_percent(tile) is None


def test_wall_hp_percent_scales_with_level(db):
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=2)
    tile = TileFactory(building=building, wall_hitpoints=100)

    assert wall_hp_percent(tile) == 50
