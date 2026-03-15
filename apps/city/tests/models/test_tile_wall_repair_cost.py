import pytest

from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory


@pytest.mark.django_db
def test_wall_repair_cost_returns_none_for_non_wall_tile():
    tile = TileFactory(building=None, wall_hitpoints=None)

    assert tile.wall_repair_cost is None


@pytest.mark.django_db
def test_wall_repair_cost_returns_none_when_hitpoints_is_none():
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(building=building, wall_hitpoints=None)

    assert tile.wall_repair_cost is None


@pytest.mark.django_db
def test_wall_repair_cost_returns_zero_when_fully_healthy():
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(building=building, wall_hitpoints=100)

    assert tile.wall_repair_cost == 0


@pytest.mark.django_db
def test_wall_repair_cost_equals_building_costs_when_fully_damaged():
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(building=building, wall_hitpoints=0)

    assert tile.wall_repair_cost == 100


@pytest.mark.django_db
def test_wall_repair_cost_is_proportional_when_half_damaged():
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(building=building, wall_hitpoints=50)

    assert tile.wall_repair_cost == 50


@pytest.mark.django_db
def test_wall_repair_cost_scales_with_building_costs():
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=200)
    tile = TileFactory(building=building, wall_hitpoints=0)

    assert tile.wall_repair_cost == 200
