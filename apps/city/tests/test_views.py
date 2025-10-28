import json
from unittest import mock

import pytest
from django.test import RequestFactory
from django.urls import reverse

from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
)
from apps.city.views import (
    TileBuildView,
    TileDemolishView,
)
from apps.savegame.tests.factories import SavegameFactory


# BalanceView Tests
@pytest.mark.django_db
def test_balance_view_response(authenticated_client, user):
    """Test BalanceView responds correctly and includes balance data in context."""
    SavegameFactory(user=user, is_active=True, coins=1000)

    response = authenticated_client.get(reverse("city:balance"))

    assert response.status_code == 200
    assert "city/balance.html" in [t.name for t in response.templates]


# PrestigeView Tests
@pytest.mark.django_db
def test_prestige_view_response(authenticated_client, user):
    """Test PrestigeView responds correctly."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert "city/prestige.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_prestige_view_with_savegame(authenticated_client, user):
    """Test PrestigeView includes prestige data when savegame exists."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert "total_prestige" in response.context
    assert "prestige_breakdown" in response.context


@pytest.mark.django_db
def test_prestige_view_without_savegame(authenticated_client, user):
    """Test PrestigeView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_prestige_view_with_prestigious_buildings(authenticated_client, user):
    """Test PrestigeView calculates prestige correctly with buildings."""
    savegame = SavegameFactory(user=user, is_active=True)
    building1 = BuildingFactory.create(level=2, prestige=5)
    building2 = BuildingFactory.create(level=3, prestige=10)
    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert response.context["total_prestige"] == 15
    assert len(response.context["prestige_breakdown"]) == 2


@pytest.mark.django_db
def test_prestige_view_breakdown_structure(authenticated_client, user):
    """Test PrestigeView breakdown has correct structure."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory.create(name="Test Building", level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building, x=10, y=20)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    breakdown = response.context["prestige_breakdown"]
    assert len(breakdown) == 1
    assert breakdown[0]["building_name"] == "Test Building"
    assert breakdown[0]["level"] == 2
    assert breakdown[0]["prestige"] == 5
    assert breakdown[0]["x"] == 10
    assert breakdown[0]["y"] == 20


@pytest.mark.django_db
def test_prestige_view_no_prestige_buildings(authenticated_client, user):
    """Test PrestigeView with buildings that have no prestige."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory.create(level=1, prestige=0)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert response.context["total_prestige"] == 0
    assert len(response.context["prestige_breakdown"]) == 0


@pytest.mark.django_db
def test_prestige_view_breakdown_ordered_by_prestige(authenticated_client, user):
    """Test PrestigeView breakdown is ordered by prestige descending."""
    savegame = SavegameFactory(user=user, is_active=True)
    building1 = BuildingFactory.create(name="Low Prestige", level=2, prestige=3)
    building2 = BuildingFactory.create(name="High Prestige", level=3, prestige=10)
    building3 = BuildingFactory.create(name="Medium Prestige", level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)
    TileFactory.create(savegame=savegame, building=building3)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    breakdown = response.context["prestige_breakdown"]
    assert len(breakdown) == 3
    assert breakdown[0]["building_name"] == "High Prestige"
    assert breakdown[1]["building_name"] == "Medium Prestige"
    assert breakdown[2]["building_name"] == "Low Prestige"


# DefensesView Tests
@pytest.mark.django_db
def test_defenses_view_response(authenticated_client, user):
    """Test DefensesView responds correctly and includes breakdown in context."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:defenses"))

    assert response.status_code == 200
    assert "city/defenses.html" in [t.name for t in response.templates]
    assert "breakdown" in response.context


@pytest.mark.django_db
def test_defenses_view_with_savegame(authenticated_client, user):
    """Test DefensesView includes defense breakdown when savegame exists."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:defenses"))

    assert response.status_code == 200
    assert "breakdown" in response.context
    breakdown = response.context["breakdown"]
    # Verify breakdown has expected attributes (from DefenseBreakdown dataclass)
    assert hasattr(breakdown, "is_enclosed")
    assert hasattr(breakdown, "base_defense")
    assert hasattr(breakdown, "shape_bonus")
    assert hasattr(breakdown, "spike_malus")
    assert hasattr(breakdown, "potential_total")
    assert hasattr(breakdown, "actual_total")


@pytest.mark.django_db
def test_defenses_view_without_savegame(authenticated_client, user):
    """Test DefensesView redirects when no active savegame exists."""
    # Don't create a savegame for this user
    response = authenticated_client.get(reverse("city:defenses"))

    # View should redirect to savegame list (SavegameRequiredMixin behavior)
    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


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
    tile = TileFactory.create()

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
    tile = TileFactory.create()
    building = BuildingFactory(building_costs=50)

    # Create mock form with cleaned data
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": building}
    mock_form.initial = {"current_building": None}  # No initial building

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
    tile = TileFactory.create()

    # Create mock form with no building
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": None}
    mock_form.initial = {"current_building": None}  # No initial building

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
def test_tile_build_view_form_valid_demolish_with_costs(request_factory, user):
    """Test TileBuildView charges demolition costs when demolishing via form."""
    savegame = SavegameFactory(user=user, is_active=True, coins=100)
    tile = TileFactory.create()
    old_building = BuildingFactory(demolition_costs=25)

    # Create mock form that demolishes (sets building to None)
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": None}
    mock_form.initial = {"current_building": old_building}

    request = request_factory.get("/")
    request.user = user
    view = TileBuildView()
    view.object = tile
    view.request = request

    with mock.patch("apps.city.views.generic.UpdateView.form_valid") as mock_super_form_valid:
        mock_super_form_valid.return_value = mock.Mock()

        response = view.form_valid(mock_form)

        # Verify demolition costs were charged
        savegame.refresh_from_db()
        assert savegame.coins == 75  # 100 - 25 = 75

        # Verify response headers
        assert response.status_code == 200


@pytest.mark.django_db
def test_tile_build_view_get_success_url():
    """Test TileBuildView returns None for success URL."""
    view = TileBuildView()
    assert view.get_success_url() is None


@pytest.mark.django_db
def test_tile_build_view_post_request(client):
    """Test TileBuildView handles POST request."""
    terrain = TerrainFactory.create()
    building_type = BuildingTypeFactory.create()
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
    terrain = TerrainFactory.create()
    building_type = BuildingTypeFactory.create()
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
