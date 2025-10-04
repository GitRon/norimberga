from unittest import mock

import pytest
from django.test import Client
from django.urls import reverse

from apps.city.models import Savegame, Tile
from apps.city.tests.factories import SavegameFactory, TerrainFactory, UserFactory


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


# SavegameListView Tests
@pytest.mark.django_db
def test_savegame_list_view_shows_user_savegames(client):
    """Test SavegameListView displays only the user's savegames."""
    user = UserFactory()
    other_user = UserFactory()
    client.force_login(user)

    user_savegame1 = SavegameFactory(user=user, city_name="User City 1")
    user_savegame2 = SavegameFactory(user=user, city_name="User City 2")
    SavegameFactory(user=other_user, city_name="Other City")

    response = client.get(reverse("city:savegame-list"))

    assert response.status_code == 200
    assert user_savegame1 in response.context["savegames"]
    assert user_savegame2 in response.context["savegames"]
    assert len(response.context["savegames"]) == 2


@pytest.mark.django_db
def test_savegame_list_view_orders_by_id_desc(client):
    """Test SavegameListView orders savegames by ID descending."""
    user = UserFactory()
    client.force_login(user)

    savegame1 = SavegameFactory(user=user)
    savegame2 = SavegameFactory(user=user)
    savegame3 = SavegameFactory(user=user)

    response = client.get(reverse("city:savegame-list"))

    savegames = list(response.context["savegames"])
    assert savegames[0] == savegame3
    assert savegames[1] == savegame2
    assert savegames[2] == savegame1


@pytest.mark.django_db
def test_savegame_list_view_requires_authentication(client):
    """Test SavegameListView requires user to be logged in."""
    response = client.get(reverse("city:savegame-list"))

    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_savegame_list_view_template(client):
    """Test SavegameListView uses correct template."""
    user = UserFactory()
    client.force_login(user)

    response = client.get(reverse("city:savegame-list"))

    assert "city/savegame_list.html" in [t.name for t in response.templates]


# SavegameLoadView Tests
@pytest.mark.django_db
def test_savegame_load_view_sets_savegame_active(client):
    """Test SavegameLoadView activates the selected savegame."""
    user = UserFactory()
    client.force_login(user)

    active_savegame = SavegameFactory(user=user, is_active=True)
    inactive_savegame = SavegameFactory(user=user, is_active=False)

    response = client.post(reverse("city:savegame-load", kwargs={"pk": inactive_savegame.pk}))

    # Verify response
    assert response.status_code == 200
    assert response["HX-Redirect"] == reverse("city:landing-page")

    # Verify savegame states
    active_savegame.refresh_from_db()
    inactive_savegame.refresh_from_db()
    assert active_savegame.is_active is False
    assert inactive_savegame.is_active is True


@pytest.mark.django_db
def test_savegame_load_view_requires_authentication(client):
    """Test SavegameLoadView requires user to be logged in."""
    savegame = SavegameFactory()

    response = client.post(reverse("city:savegame-load", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_savegame_load_view_only_loads_own_savegames(client):
    """Test SavegameLoadView doesn't load other users' savegames."""
    user = UserFactory()
    other_user = UserFactory()
    client.force_login(user)

    other_savegame = SavegameFactory(user=other_user, is_active=False)

    with pytest.raises(Savegame.DoesNotExist):
        client.post(reverse("city:savegame-load", kwargs={"pk": other_savegame.pk}))


@pytest.mark.django_db
def test_savegame_load_view_deactivates_all_other_savegames(client):
    """Test SavegameLoadView deactivates all other user savegames."""
    user = UserFactory()
    client.force_login(user)

    savegame1 = SavegameFactory(user=user, is_active=True)
    savegame2 = SavegameFactory(user=user, is_active=True)
    savegame3 = SavegameFactory(user=user, is_active=False)

    client.post(reverse("city:savegame-load", kwargs={"pk": savegame3.pk}))

    savegame1.refresh_from_db()
    savegame2.refresh_from_db()
    savegame3.refresh_from_db()

    assert savegame1.is_active is False
    assert savegame2.is_active is False
    assert savegame3.is_active is True


# SavegameCreateView Tests
@pytest.mark.django_db
def test_savegame_create_view_get_displays_form(client):
    """Test SavegameCreateView GET displays the creation form."""
    user = UserFactory()
    client.force_login(user)

    response = client.get(reverse("city:savegame-create"))

    assert response.status_code == 200
    assert "city/savegame_create.html" in [t.name for t in response.templates]
    assert "form" in response.context


@pytest.mark.django_db
def test_savegame_create_view_creates_savegame(client):
    """Test SavegameCreateView creates a new savegame for the user."""
    user = UserFactory()
    client.force_login(user)

    initial_count = Savegame.objects.filter(user=user).count()

    with mock.patch("apps.city.views.MapGenerationService") as mock_service:
        mock_instance = mock_service.return_value
        response = client.post(reverse("city:savegame-create"), {"city_name": "Test City"})

        assert response.status_code == 302
        assert response.url == reverse("city:landing-page")

        # Verify new savegame was created
        assert Savegame.objects.filter(user=user).count() == initial_count + 1

        # Verify map generation was called
        mock_service.assert_called_once()
        mock_instance.process.assert_called_once()


@pytest.mark.django_db
def test_savegame_create_view_generates_map(client):
    """Test SavegameCreateView calls MapGenerationService."""
    user = UserFactory()
    client.force_login(user)

    with mock.patch("apps.city.views.MapGenerationService") as mock_service:
        mock_instance = mock_service.return_value

        client.post(reverse("city:savegame-create"), {"city_name": "Test City"})

        # Verify service was instantiated with the new savegame
        mock_service.assert_called_once()
        call_args = mock_service.call_args
        assert "savegame" in call_args.kwargs
        assert isinstance(call_args.kwargs["savegame"], Savegame)
        assert call_args.kwargs["savegame"].user == user

        # Verify process was called
        mock_instance.process.assert_called_once()


@pytest.mark.django_db
def test_savegame_create_view_integration_with_map_generation(client):
    """Test SavegameCreateView integration with real MapGenerationService."""
    user = UserFactory()
    client.force_login(user)

    # Create required terrain for map generation
    TerrainFactory(name="River", probability=1)
    TerrainFactory(name="Plains", probability=50)

    initial_count = Savegame.objects.filter(user=user).count()

    response = client.post(reverse("city:savegame-create"), {"city_name": "Integration Test City"})

    assert response.status_code == 302
    assert Savegame.objects.filter(user=user).count() == initial_count + 1

    # Verify tiles were created
    new_savegame = Savegame.objects.filter(user=user).order_by("-id").first()
    assert Tile.objects.filter(savegame=new_savegame).count() > 0


@pytest.mark.django_db
def test_savegame_create_view_requires_authentication(client):
    """Test SavegameCreateView requires user to be logged in."""
    response = client.post(reverse("city:savegame-create"))

    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_savegame_create_view_assigns_savegame_to_user(client):
    """Test SavegameCreateView assigns new savegame to current user."""
    user = UserFactory()
    client.force_login(user)

    with mock.patch("apps.city.views.MapGenerationService"):
        client.post(reverse("city:savegame-create"), {"city_name": "Test City"})

        new_savegame = Savegame.objects.filter(user=user).order_by("-id").first()
        assert new_savegame.user == user


@pytest.mark.django_db
def test_savegame_create_view_sets_city_name(client):
    """Test SavegameCreateView sets the city name from form."""
    user = UserFactory()
    client.force_login(user)

    with mock.patch("apps.city.views.MapGenerationService"):
        client.post(reverse("city:savegame-create"), {"city_name": "My Medieval City"})

        new_savegame = Savegame.objects.filter(user=user).order_by("-id").first()
        assert new_savegame.city_name == "My Medieval City"


@pytest.mark.django_db
def test_savegame_create_view_sets_new_savegame_as_active(client):
    """Test SavegameCreateView sets the new savegame as active."""
    user = UserFactory()
    client.force_login(user)

    # Create existing active savegame
    existing_savegame = SavegameFactory(user=user, is_active=True)

    with mock.patch("apps.city.views.MapGenerationService"):
        client.post(reverse("city:savegame-create"), {"city_name": "Test City"})

        # Verify old savegame is no longer active
        existing_savegame.refresh_from_db()
        assert existing_savegame.is_active is False

        # Verify new savegame is active
        new_savegame = Savegame.objects.filter(user=user).order_by("-id").first()
        assert new_savegame.is_active is True


# SavegameDeleteView Tests
@pytest.mark.django_db
def test_savegame_delete_view_deletes_inactive_savegame(client):
    """Test SavegameDeleteView deletes inactive savegame."""
    user = UserFactory()
    client.force_login(user)

    savegame = SavegameFactory(user=user, is_active=False)

    response = client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert not Savegame.objects.filter(pk=savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_cannot_delete_active_savegame(client):
    """Test SavegameDeleteView cannot delete active savegame."""
    user = UserFactory()
    client.force_login(user)

    savegame = SavegameFactory(user=user, is_active=True)

    response = client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    # Should return 404 since queryset excludes active savegames
    assert response.status_code == 404

    # Verify savegame still exists
    assert Savegame.objects.filter(pk=savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_cannot_delete_other_users_savegame(client):
    """Test SavegameDeleteView cannot delete other user's savegame."""
    user = UserFactory()
    other_user = UserFactory()
    client.force_login(user)

    other_savegame = SavegameFactory(user=other_user, is_active=False)

    response = client.delete(reverse("city:savegame-delete", kwargs={"pk": other_savegame.pk}))

    # Should return 404 since queryset only includes own savegames
    assert response.status_code == 404

    # Verify savegame still exists
    assert Savegame.objects.filter(pk=other_savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_requires_authentication(client):
    """Test SavegameDeleteView requires user to be logged in."""
    savegame = SavegameFactory(is_active=False)

    response = client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert "/login/" in response.url


@pytest.mark.django_db
def test_savegame_delete_view_redirects_to_list(client):
    """Test SavegameDeleteView redirects to savegame list on success."""
    user = UserFactory()
    client.force_login(user)

    savegame = SavegameFactory(user=user, is_active=False)

    response = client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert response.url == reverse("city:savegame-list")
