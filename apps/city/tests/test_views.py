import json
from unittest import mock

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    SavegameFactory,
    TerrainFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
)
from apps.city.views import (
    BalanceView,
    TileBuildView,
    TileDemolishView,
)


# SavegameValueView Tests
@pytest.mark.django_db
def test_savegame_value_view_response(authenticated_client, user):
    """Test SavegameValueView responds correctly."""
    savegame = SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:savegame-value", kwargs={"pk": savegame.pk}))

    assert response.status_code == 200
    assert "savegame/partials/_nav_values.html" in [t.name for t in response.templates]


# NavbarValuesView Tests
@pytest.mark.django_db
def test_navbar_values_view_response(authenticated_client, user):
    """Test NavbarValuesView returns correct template."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:navbar-values"))

    assert response.status_code == 200
    assert "partials/_navbar_values.html" in [t.name for t in response.templates]


# LandingPageView Tests
@pytest.mark.django_db
def test_landing_page_view_response(authenticated_client, user):
    """Test LandingPageView responds correctly."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:landing-page"))

    assert response.status_code == 200
    assert "city/landing_page.html" in [t.name for t in response.templates]


# CityMapView Tests
@pytest.mark.django_db
def test_city_map_view_response(authenticated_client):
    """Test CityMapView responds correctly."""
    response = authenticated_client.get(reverse("city:city-map"))

    assert response.status_code == 200
    assert "city/partials/city/_city_map.html" in [t.name for t in response.templates]


# CityMessagesView Tests
@pytest.mark.django_db
def test_city_messages_view_response(authenticated_client):
    """Test CityMessagesView responds correctly."""
    response = authenticated_client.get(reverse("city:city-messages"))

    assert response.status_code == 200
    assert "city/partials/city/_messages.html" in [t.name for t in response.templates]


# TileBuildView Tests
@pytest.mark.django_db
def test_tile_build_view_get_form_kwargs(request_factory, user):
    """Test TileBuildView adds savegame to form kwargs."""
    savegame = SavegameFactory(user=user, is_active=True)
    tile = TileFactory()

    request = request_factory.get("/")
    request.user = user
    view = TileBuildView()
    view.request = request
    view.object = tile

    form_kwargs = view.get_form_kwargs()

    assert "savegame" in form_kwargs
    assert form_kwargs["savegame"] == savegame


@pytest.mark.django_db
def test_tile_build_view_form_valid_with_building(request_factory, user):
    """Test TileBuildView deducts coins when building is selected."""
    savegame = SavegameFactory(user=user, coins=100, is_active=True)
    tile = TileFactory()
    building = BuildingFactory(building_costs=50)

    # Create mock form with cleaned data
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": building}

    request = request_factory.get("/")
    request.user = user
    view = TileBuildView()
    view.object = tile
    view.request = request

    with mock.patch("apps.city.views.generic.UpdateView.form_valid") as mock_super_form_valid:
        mock_super_form_valid.return_value = mock.Mock()

        response = view.form_valid(mock_form)

        # Verify coins were deducted
        savegame.refresh_from_db()
        assert savegame.coins == 50

        # Verify response headers
        assert response.status_code == 200
        hx_trigger = json.loads(response["HX-Trigger"])
        assert "refreshMap" in hx_trigger
        assert "updateNavbarValues" in hx_trigger


@pytest.mark.django_db
def test_tile_build_view_form_valid_without_building(request_factory, user):
    """Test TileBuildView doesn't deduct coins when no building selected."""
    savegame = SavegameFactory(user=user, is_active=True, coins=100)
    tile = TileFactory()

    # Create mock form with no building
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": None}

    request = request_factory.get("/")
    request.user = user
    view = TileBuildView()
    view.object = tile
    view.request = request

    with mock.patch("apps.city.views.generic.UpdateView.form_valid") as mock_super_form_valid:
        mock_super_form_valid.return_value = mock.Mock()

        response = view.form_valid(mock_form)

        # Verify coins weren't deducted
        savegame.refresh_from_db()
        assert savegame.coins == 100

        # Verify response headers still set
        assert response.status_code == 200


@pytest.mark.django_db
def test_tile_build_view_get_success_url():
    """Test TileBuildView returns None for success URL."""
    view = TileBuildView()
    assert view.get_success_url() is None


@pytest.mark.django_db
def test_tile_build_view_post_request(client):
    """Test TileBuildView handles POST request."""
    terrain = TerrainFactory()
    building_type = BuildingTypeFactory()
    building_type.allowed_terrains.add(terrain)
    building = BuildingFactory(building_type=building_type, building_costs=50, level=1)

    savegame = SavegameFactory(coins=100)
    tile = TileFactory(savegame=savegame, terrain=terrain)

    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=True):
        response = client.post(reverse("city:tile-build", kwargs={"pk": tile.pk}), data={"building": building.pk})

        # Should redirect or return success status
        assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_tile_build_view_post_request_authenticated(authenticated_client, user):
    """Test TileBuildView handles authenticated POST request."""
    terrain = TerrainFactory()
    building_type = BuildingTypeFactory()
    building_type.allowed_terrains.add(terrain)
    building = BuildingFactory(building_type=building_type, building_costs=50, level=1)

    savegame = SavegameFactory(user=user, coins=100, is_active=True)
    tile = TileFactory(savegame=savegame, terrain=terrain)

    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=True):
        response = authenticated_client.post(
            reverse("city:tile-build", kwargs={"pk": tile.pk}), data={"building": building.pk}
        )

        # Should redirect or return success status
        assert response.status_code in [200, 302]


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
def test_tile_demolish_view_post_unique_building():
    """Test TileDemolishView fails to demolish unique building."""
    unique_building_type = UniqueBuildingTypeFactory()
    unique_building = BuildingFactory(building_type=unique_building_type)
    tile = TileFactory(building=unique_building)

    view = TileDemolishView()
    request = RequestFactory().post("/")

    response = view.post(request, pk=tile.pk)

    # Verify building was not removed
    tile.refresh_from_db()
    assert tile.building == unique_building

    # Verify error response
    assert response.status_code == 400
    assert b"Cannot demolish unique buildings" in response.content


@pytest.mark.django_db
def test_tile_demolish_view_post_no_building():
    """Test TileDemolishView handles tile with no building."""
    tile = TileFactory(building=None)

    view = TileDemolishView()
    request = RequestFactory().post("/")

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

    unique_building_type = UniqueBuildingTypeFactory()
    unique_building = BuildingFactory(building_type=unique_building_type)
    tile = TileFactory(building=unique_building)

    response = authenticated_client.post(reverse("city:tile-demolish", kwargs={"pk": tile.pk}))

    # Verify building was not removed
    tile.refresh_from_db()
    assert tile.building == unique_building

    # Verify error response
    assert response.status_code == 400


# BalanceView Tests
@pytest.mark.django_db
def test_balance_view_get_context_data(request_factory, user):
    """Test BalanceView includes balance data in context."""
    savegame = SavegameFactory(user=user, is_active=True)

    # Create buildings with known values
    building1 = BuildingFactory(taxes=30, maintenance_costs=10)
    building2 = BuildingFactory(taxes=20, maintenance_costs=5)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)

    request = request_factory.get("/")
    request.user = user
    view = BalanceView()
    view.request = request
    context = view.get_context_data()

    assert context["savegame"] == savegame
    assert context["taxes"] == 50  # 30 + 20
    assert context["maintenance"] == 15  # 10 + 5
    assert context["balance"] == 35  # 50 - 15
    assert "tax_by_building_type" in context
    assert "maintenance_by_building_type" in context


@pytest.mark.django_db
def test_balance_view_response(authenticated_client, user):
    """Test BalanceView responds correctly."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory(taxes=20, maintenance_costs=10)
    TileFactory(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("city:balance"))

    assert response.status_code == 200
    assert "city/balance.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_balance_view_context_with_no_buildings(authenticated_client, user):
    """Test BalanceView handles savegame with no buildings."""
    savegame = SavegameFactory(user=user, is_active=True)
    TileFactory(savegame=savegame, building=None)

    response = authenticated_client.get(reverse("city:balance"))

    assert response.status_code == 200
    assert response.context["taxes"] == 0
    assert response.context["maintenance"] == 0
    assert response.context["balance"] == 0


@pytest.mark.django_db
def test_balance_view_context_positive_balance(authenticated_client, user):
    """Test BalanceView displays positive balance correctly."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory(taxes=100, maintenance_costs=20)
    TileFactory(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("city:balance"))

    assert response.status_code == 200
    assert response.context["balance"] == 80
    assert response.context["balance"] > 0


@pytest.mark.django_db
def test_balance_view_context_negative_balance(authenticated_client, user):
    """Test BalanceView displays negative balance correctly."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory(taxes=10, maintenance_costs=50)
    TileFactory(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("city:balance"))

    assert response.status_code == 200
    assert response.context["balance"] == -40
    assert response.context["balance"] < 0


@pytest.mark.django_db
def test_balance_view_template_name():
    """Test BalanceView uses correct template."""
    view = BalanceView()
    assert view.template_name == "city/balance.html"
