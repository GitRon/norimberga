import json

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
)
from apps.city.views import TileDemolishView
from apps.savegame.tests.factories import SavegameFactory


# TileDemolishView Tests
@pytest.mark.django_db
def test_tile_demolish_view_post_success(user):
    """Test TileDemolishView successfully demolishes building."""
    SavegameFactory(user=user, is_active=True)

    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    view = TileDemolishView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    # Verify building was removed
    tile.refresh_from_db()
    assert tile.building is None

    # Verify response
    assert response.status_code == 200
    hx_trigger = json.loads(response["HX-Trigger"])
    assert "refreshMap" in hx_trigger
    assert "updateNavbarValues" in hx_trigger


@pytest.mark.django_db
def test_tile_demolish_view_post_unique_building(user):
    """Test TileDemolishView fails to demolish unique building."""
    SavegameFactory(user=user, is_active=True)
    unique_building_type = UniqueBuildingTypeFactory.create()
    unique_building = BuildingFactory(building_type=unique_building_type)
    tile = TileFactory(building=unique_building)

    view = TileDemolishView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    # Verify building was not removed
    tile.refresh_from_db()
    assert tile.building == unique_building

    # Verify error response
    assert response.status_code == 400
    assert b"Cannot demolish unique buildings" in response.content


@pytest.mark.django_db
def test_tile_demolish_view_post_no_building(user):
    """Test TileDemolishView handles tile with no building."""
    SavegameFactory(user=user, is_active=True)
    tile = TileFactory(building=None)

    view = TileDemolishView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    # Verify tile still has no building
    tile.refresh_from_db()
    assert tile.building is None

    # Should still return success
    assert response.status_code == 200


@pytest.mark.django_db
def test_tile_demolish_view_post_request(authenticated_client, user):
    """Test TileDemolishView handles POST request via client."""
    SavegameFactory(user=user, is_active=True)

    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    response = authenticated_client.post(reverse("city:tile-demolish", kwargs={"pk": tile.pk}))

    # Verify building was removed
    tile.refresh_from_db()
    assert tile.building is None

    # Verify successful response
    assert response.status_code == 200


@pytest.mark.django_db
def test_tile_demolish_view_post_unique_building_via_client(authenticated_client, user):
    """Test TileDemolishView rejects unique building demolition via client."""
    SavegameFactory(user=user, is_active=True)

    unique_building_type = UniqueBuildingTypeFactory.create()
    unique_building = BuildingFactory(building_type=unique_building_type)
    tile = TileFactory(building=unique_building)

    response = authenticated_client.post(reverse("city:tile-demolish", kwargs={"pk": tile.pk}))

    # Verify building was not removed
    tile.refresh_from_db()
    assert tile.building == unique_building

    # Verify error response
    assert response.status_code == 400


@pytest.mark.django_db
def test_tile_demolish_view_charges_demolition_costs(user):
    """Test TileDemolishView charges demolition costs."""
    savegame = SavegameFactory(user=user, is_active=True, coins=100)

    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type, demolition_costs=30)
    tile = TileFactory(building=building, savegame=savegame)

    view = TileDemolishView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    # Verify building was removed
    tile.refresh_from_db()
    assert tile.building is None

    # Verify coins were charged
    savegame.refresh_from_db()
    assert savegame.coins == 70  # 100 - 30 = 70

    # Verify response
    assert response.status_code == 200


@pytest.mark.django_db
def test_tile_demolish_view_insufficient_coins_for_demolition(user):
    """Test TileDemolishView rejects demolition when insufficient coins."""
    savegame = SavegameFactory(user=user, is_active=True, coins=10)

    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type, demolition_costs=30)
    tile = TileFactory(building=building, savegame=savegame)

    view = TileDemolishView()
    request = RequestFactory().post("/")
    request.user = user

    response = view.post(request, pk=tile.pk)

    # Verify building was NOT removed
    tile.refresh_from_db()
    assert tile.building == building

    # Verify coins were not charged
    savegame.refresh_from_db()
    assert savegame.coins == 10

    # Verify error response
    assert response.status_code == 400
    assert b"Not enough coins" in response.content
