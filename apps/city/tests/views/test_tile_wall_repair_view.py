import json

import pytest
from django.test import RequestFactory

from apps.city.constants import WALL_REPAIR_COST_PER_HP
from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory, TileFactory, WallBuildingTypeFactory
from apps.city.views.tile_wall_repair_view import TileWallRepairView
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_tile_wall_repair_view_post_success(user):
    """Test repair restores HP and charges coins."""
    savegame = SavegameFactory.create(user=user, is_active=True, coins=500)
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=60)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    assert response.status_code == 200
    tile.refresh_from_db()
    assert tile.wall_hitpoints == 100

    savegame.refresh_from_db()
    expected_cost = (100 - 60) * WALL_REPAIR_COST_PER_HP
    assert savegame.coins == 500 - expected_cost


@pytest.mark.django_db
def test_tile_wall_repair_view_post_triggers_htmx(user):
    """Test repair response includes expected HX-Trigger headers."""
    savegame = SavegameFactory.create(user=user, is_active=True, coins=1000)
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=50)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    hx_trigger = json.loads(response["HX-Trigger"])
    assert "refreshMap" in hx_trigger
    assert "updateNavbarValues" in hx_trigger


@pytest.mark.django_db
def test_tile_wall_repair_view_post_not_enough_coins(user):
    """Test repair fails when savegame does not have enough coins."""
    savegame = SavegameFactory.create(user=user, is_active=True, coins=5)
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=50)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    assert response.status_code == 400
    tile.refresh_from_db()
    assert tile.wall_hitpoints == 50  # unchanged


@pytest.mark.django_db
def test_tile_wall_repair_view_post_already_full_hp(user):
    """Test repair fails when wall is already at full HP."""
    savegame = SavegameFactory.create(user=user, is_active=True, coins=1000)
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    assert response.status_code == 400
    savegame.refresh_from_db()
    assert savegame.coins == 1000  # no charge


@pytest.mark.django_db
def test_tile_wall_repair_view_post_non_wall_tile(user):
    """Test repair fails for non-wall tiles."""
    savegame = SavegameFactory.create(user=user, is_active=True, coins=1000)
    city_type = BuildingTypeFactory.create(is_city=True, is_wall=False)
    building = BuildingFactory.create(building_type=city_type)
    tile = TileFactory.create(savegame=savegame, building=building)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    assert response.status_code == 400


@pytest.mark.django_db
def test_tile_wall_repair_view_post_rejects_foreign_tile(user):
    """Test repair fails when the tile does not belong to the user's savegame."""
    SavegameFactory.create(user=user, is_active=True, coins=1000)
    other_savegame = SavegameFactory.create(is_active=True, coins=1000)
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=1)
    foreign_tile = TileFactory.create(savegame=other_savegame, building=building, wall_hitpoints=60)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=foreign_tile.pk)

    assert response.status_code == 404
    foreign_tile.refresh_from_db()
    assert foreign_tile.wall_hitpoints == 60  # unchanged


@pytest.mark.django_db
def test_tile_wall_repair_view_post_level2_wall(user):
    """Test repair cost scales with wall level."""
    savegame = SavegameFactory.create(user=user, is_active=True, coins=2000)
    wall_type = WallBuildingTypeFactory.create()
    building = BuildingFactory.create(building_type=wall_type, level=2)
    tile = TileFactory.create(savegame=savegame, building=building, wall_hitpoints=100)

    view = TileWallRepairView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    assert response.status_code == 200
    tile.refresh_from_db()
    assert tile.wall_hitpoints == 200  # max HP for level 2

    savegame.refresh_from_db()
    expected_cost = (200 - 100) * WALL_REPAIR_COST_PER_HP
    assert savegame.coins == 2000 - expected_cost
