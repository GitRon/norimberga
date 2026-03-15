import pytest
from django.urls import reverse

from apps.city.tests.factories import BuildingFactory, TileFactory, WallBuildingTypeFactory
from apps.city.views.wall_repair_all_view import WallRepairAllView
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_post_repairs_all_walls_successfully(request_factory, user):
    savegame = SavegameFactory(user=user, coins=500)
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    tile = TileFactory(savegame=savegame, building=building, wall_hitpoints=0)

    request = request_factory.post(reverse("city:wall-repair-all"))
    request.user = user

    response = WallRepairAllView.as_view()(request)

    assert response.status_code == 200
    tile.refresh_from_db()
    assert tile.wall_hitpoints == 100


@pytest.mark.django_db
def test_post_returns_bad_request_when_not_enough_coins(request_factory, user):
    savegame = SavegameFactory(user=user, coins=10)
    wall_building_type = WallBuildingTypeFactory()
    building = BuildingFactory(building_type=wall_building_type, level=1, building_costs=100)
    TileFactory(savegame=savegame, building=building, wall_hitpoints=0)

    request = request_factory.post(reverse("city:wall-repair-all"))
    request.user = user

    response = WallRepairAllView.as_view()(request)

    assert response.status_code == 400
