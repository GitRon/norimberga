import json
from unittest import mock

import pytest
from django.urls import reverse

from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    TerrainFactory,
    TileFactory,
)
from apps.city.views import TileBuildView
from apps.savegame.tests.factories import SavegameFactory


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

    with mock.patch("apps.city.views.tile_build_view.generic.UpdateView.form_valid") as mock_super_form_valid:
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

    with mock.patch("apps.city.views.tile_build_view.generic.UpdateView.form_valid") as mock_super_form_valid:
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

    with mock.patch("apps.city.views.tile_build_view.generic.UpdateView.form_valid") as mock_super_form_valid:
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
