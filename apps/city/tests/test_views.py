import json
from unittest import mock

import pytest
from django.test import Client, RequestFactory
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
    LandingPageView,
    SavegameValueView,
    TileBuildView,
    TileDemolishView,
)


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def request_factory():
    """Provide Django request factory."""
    return RequestFactory()


# SavegameValueView Tests
@pytest.mark.django_db
def test_savegame_value_view_get_context_data():
    """Test SavegameValueView includes max_housing_space in context."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.views.BuildingHousingService") as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.calculate_max_space.return_value = 50

        view = SavegameValueView()
        view.object = savegame

        context = view.get_context_data()

        assert context["max_housing_space"] == 50
        mock_service.assert_called_once()
        mock_instance.calculate_max_space.assert_called_once()


@pytest.mark.django_db
def test_savegame_value_view_response(client):
    """Test SavegameValueView responds correctly."""
    savegame = SavegameFactory()

    with mock.patch("apps.city.views.BuildingHousingService"):
        response = client.get(reverse("city:savegame-value", kwargs={"pk": savegame.pk}))

        assert response.status_code == 200
        assert "savegame/partials/_nav_values.html" in [t.name for t in response.templates]


# LandingPageView Tests
@pytest.mark.django_db
def test_landing_page_view_get_context_data():
    """Test LandingPageView includes max_housing_space in context."""
    with mock.patch("apps.city.views.BuildingHousingService") as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.calculate_max_space.return_value = 75

        view = LandingPageView()
        context = view.get_context_data()

        assert context["max_housing_space"] == 75
        mock_service.assert_called_once()
        mock_instance.calculate_max_space.assert_called_once()


@pytest.mark.django_db
def test_landing_page_view_response(client):
    """Test LandingPageView responds correctly."""
    with mock.patch("apps.city.views.BuildingHousingService"):
        response = client.get(reverse("city:landing-page"))

        assert response.status_code == 200
        assert "city/landing_page.html" in [t.name for t in response.templates]


# CityMapView Tests
@pytest.mark.django_db
def test_city_map_view_response(client):
    """Test CityMapView responds correctly."""
    response = client.get(reverse("city:city-map"))

    assert response.status_code == 200
    assert "city/partials/city/_city_map.html" in [t.name for t in response.templates]


# CityMessagesView Tests
@pytest.mark.django_db
def test_city_messages_view_response(client):
    """Test CityMessagesView responds correctly."""
    response = client.get(reverse("city:city-messages"))

    assert response.status_code == 200
    assert "city/partials/city/_messages.html" in [t.name for t in response.templates]


# TileBuildView Tests
@pytest.mark.django_db
def test_tile_build_view_get_form_kwargs(request_factory):
    """Test TileBuildView adds savegame to form kwargs."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)
    tile = TileFactory()

    request = request_factory.get("/")
    view = TileBuildView()
    view.request = request
    view.object = tile

    form_kwargs = view.get_form_kwargs()

    assert "savegame" in form_kwargs
    assert form_kwargs["savegame"] == savegame


@pytest.mark.django_db
def test_tile_build_view_get_form_kwargs_creates_savegame(request_factory):
    """Test TileBuildView creates savegame if doesn't exist."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    tile = TileFactory()

    request = request_factory.get("/")
    view = TileBuildView()
    view.request = request
    view.object = tile

    form_kwargs = view.get_form_kwargs()

    assert "savegame" in form_kwargs
    assert form_kwargs["savegame"].id == 1


@pytest.mark.django_db
def test_tile_build_view_form_valid_with_building():
    """Test TileBuildView deducts coins when building is selected."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1, coins=100)
    tile = TileFactory()
    building = BuildingFactory(building_costs=50)

    # Create mock form with cleaned data
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": building}

    view = TileBuildView()
    view.object = tile

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
def test_tile_build_view_form_valid_without_building():
    """Test TileBuildView doesn't deduct coins when no building selected."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1, coins=100)
    tile = TileFactory()

    # Create mock form with no building
    mock_form = mock.Mock()
    mock_form.cleaned_data = {"building": None}

    view = TileBuildView()
    view.object = tile

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

    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1, coins=100)
    tile = TileFactory(savegame=savegame, terrain=terrain)

    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=True):
        response = client.post(reverse("city:tile-build", kwargs={"pk": tile.pk}), data={"building": building.pk})

        # Should redirect or return success status
        assert response.status_code in [200, 302]


# TileDemolishView Tests
@pytest.mark.django_db
def test_tile_demolish_view_post_success():
    """Test TileDemolishView successfully demolishes building."""
    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    view = TileDemolishView()
    request = RequestFactory().post("/")

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
def test_tile_demolish_view_post_request(client):
    """Test TileDemolishView handles POST request via client."""
    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type)
    tile = TileFactory(building=building)

    response = client.post(reverse("city:tile-demolish", kwargs={"pk": tile.pk}))

    # Verify building was removed
    tile.refresh_from_db()
    assert tile.building is None

    # Verify successful response
    assert response.status_code == 200


@pytest.mark.django_db
def test_tile_demolish_view_post_unique_building_via_client(client):
    """Test TileDemolishView rejects unique building demolition via client."""
    unique_building_type = UniqueBuildingTypeFactory()
    unique_building = BuildingFactory(building_type=unique_building_type)
    tile = TileFactory(building=unique_building)

    response = client.post(reverse("city:tile-demolish", kwargs={"pk": tile.pk}))

    # Verify building was not removed
    tile.refresh_from_db()
    assert tile.building == unique_building

    # Verify error response
    assert response.status_code == 400
