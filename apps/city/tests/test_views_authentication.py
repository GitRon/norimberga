import pytest
from django.test import Client
from django.urls import reverse

from apps.city.models import Savegame
from apps.city.tests.factories import SavegameFactory, UserFactory


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def user():
    """Provide a test user."""
    return UserFactory(username="testuser")


@pytest.fixture
def authenticated_client(client, user):
    """Provide authenticated Django test client."""
    client.force_login(user)
    return client


# UserLoginView Tests
@pytest.mark.django_db
def test_user_login_view_get_displays_login_form(client):
    """Test UserLoginView displays login form."""
    response = client.get(reverse("city:login"))

    assert response.status_code == 200
    assert "city/login.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_user_login_view_post_with_valid_credentials(client, user):
    """Test UserLoginView logs in user with valid credentials."""
    user.set_password("testpassword123")
    user.save()

    response = client.post(
        reverse("city:login"), data={"username": "testuser", "password": "testpassword123"}, follow=True
    )

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user == user


@pytest.mark.django_db
def test_user_login_view_post_with_invalid_credentials(client, user):
    """Test UserLoginView rejects invalid credentials."""
    user.set_password("testpassword123")
    user.save()

    response = client.post(reverse("city:login"), data={"username": "testuser", "password": "wrongpassword"})

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert response.context["form"].errors


@pytest.mark.django_db
def test_user_login_view_redirects_to_landing_page_after_login(client, user):
    """Test UserLoginView redirects to landing page after successful login."""
    user.set_password("testpassword123")
    user.save()

    response = client.post(
        reverse("city:login"), data={"username": "testuser", "password": "testpassword123"}, follow=False
    )

    assert response.status_code == 302
    assert response.url == reverse("city:landing-page")


# UserLogoutView Tests
@pytest.mark.django_db
def test_user_logout_view_logs_out_user(authenticated_client, user):
    """Test UserLogoutView logs out authenticated user."""
    response = authenticated_client.post(reverse("city:logout"), follow=True)

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_user_logout_view_redirects_to_login_page(authenticated_client):
    """Test UserLogoutView redirects to login page."""
    response = authenticated_client.post(reverse("city:logout"), follow=False)

    assert response.status_code == 302
    assert response.url == reverse("city:login")


# SavegameListView Tests
@pytest.mark.django_db
def test_savegame_list_view_requires_authentication(client):
    """Test SavegameListView requires user authentication."""
    response = client.get(reverse("city:savegame-list"))

    assert response.status_code == 302
    assert reverse("city:login") in response.url


@pytest.mark.django_db
def test_savegame_list_view_displays_user_savegames(authenticated_client, user):
    """Test SavegameListView displays only user's savegames."""
    savegame1 = SavegameFactory(user=user, city_name="User City 1")
    savegame2 = SavegameFactory(user=user, city_name="User City 2")
    other_user = UserFactory(username="otheruser")
    SavegameFactory(user=other_user, city_name="Other City")

    response = authenticated_client.get(reverse("city:savegame-list"))

    assert response.status_code == 200
    assert "city/savegame_list.html" in [t.name for t in response.templates]
    savegames = list(response.context["savegames"])
    assert len(savegames) == 2
    assert savegame1 in savegames
    assert savegame2 in savegames


@pytest.mark.django_db
def test_savegame_list_view_displays_no_savegames_message(authenticated_client):
    """Test SavegameListView displays message when user has no savegames."""
    response = authenticated_client.get(reverse("city:savegame-list"))

    assert response.status_code == 200
    savegames = list(response.context["savegames"])
    assert len(savegames) == 0


@pytest.mark.django_db
def test_savegame_list_view_orders_savegames_by_id_descending(authenticated_client, user):
    """Test SavegameListView orders savegames by ID descending."""
    savegame1 = SavegameFactory(user=user, city_name="First")
    savegame2 = SavegameFactory(user=user, city_name="Second")
    savegame3 = SavegameFactory(user=user, city_name="Third")

    response = authenticated_client.get(reverse("city:savegame-list"))

    savegames = list(response.context["savegames"])
    assert savegames[0] == savegame3
    assert savegames[1] == savegame2
    assert savegames[2] == savegame1


# SavegameLoadView Tests
@pytest.mark.django_db
def test_savegame_load_view_requires_authentication(client):
    """Test SavegameLoadView requires user authentication."""
    savegame = SavegameFactory()
    response = client.post(reverse("city:savegame-load", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert reverse("city:login") in response.url


@pytest.mark.django_db
def test_savegame_load_view_sets_savegame_as_active(authenticated_client, user):
    """Test SavegameLoadView sets selected savegame as active."""
    savegame1 = SavegameFactory(user=user, is_active=True)
    savegame2 = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.post(reverse("city:savegame-load", kwargs={"pk": savegame2.pk}))

    assert response.status_code == 200
    savegame1.refresh_from_db()
    savegame2.refresh_from_db()
    assert not savegame1.is_active
    assert savegame2.is_active


@pytest.mark.django_db
def test_savegame_load_view_deactivates_all_other_savegames(authenticated_client, user):
    """Test SavegameLoadView deactivates all other savegames of user."""
    savegame1 = SavegameFactory(user=user, is_active=True)
    savegame2 = SavegameFactory(user=user, is_active=True)
    savegame3 = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.post(reverse("city:savegame-load", kwargs={"pk": savegame3.pk}))

    assert response.status_code == 200
    savegame1.refresh_from_db()
    savegame2.refresh_from_db()
    savegame3.refresh_from_db()
    assert not savegame1.is_active
    assert not savegame2.is_active
    assert savegame3.is_active


@pytest.mark.django_db
def test_savegame_load_view_redirects_to_landing_page(authenticated_client, user):
    """Test SavegameLoadView redirects to landing page via HX-Redirect."""
    savegame = SavegameFactory(user=user)

    response = authenticated_client.post(reverse("city:savegame-load", kwargs={"pk": savegame.pk}))

    assert response.status_code == 200
    assert "HX-Redirect" in response
    assert response["HX-Redirect"] == reverse("city:landing-page")


@pytest.mark.django_db
def test_savegame_load_view_only_loads_own_savegame(authenticated_client, user):
    """Test SavegameLoadView only allows loading user's own savegames."""
    other_user = UserFactory(username="otheruser")
    other_savegame = SavegameFactory(user=other_user)

    with pytest.raises(Savegame.DoesNotExist):
        authenticated_client.post(reverse("city:savegame-load", kwargs={"pk": other_savegame.pk}))


# SavegameDeleteView Tests
@pytest.mark.django_db
def test_savegame_delete_view_requires_authentication(client):
    """Test SavegameDeleteView requires user authentication."""
    savegame = SavegameFactory()
    response = client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert reverse("city:login") in response.url


@pytest.mark.django_db
def test_savegame_delete_view_deletes_inactive_savegame(authenticated_client, user):
    """Test SavegameDeleteView deletes inactive savegame."""
    savegame = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert not Savegame.objects.filter(pk=savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_cannot_delete_active_savegame(authenticated_client, user):
    """Test SavegameDeleteView cannot delete active savegame."""
    savegame = SavegameFactory(user=user, is_active=True)

    response = authenticated_client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 404
    assert Savegame.objects.filter(pk=savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_cannot_delete_other_users_savegame(authenticated_client, user):
    """Test SavegameDeleteView cannot delete other user's savegame."""
    other_user = UserFactory(username="otheruser")
    other_savegame = SavegameFactory(user=other_user, is_active=False)

    response = authenticated_client.delete(reverse("city:savegame-delete", kwargs={"pk": other_savegame.pk}))

    assert response.status_code == 404
    assert Savegame.objects.filter(pk=other_savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_redirects_to_savegame_list(authenticated_client, user):
    """Test SavegameDeleteView redirects to savegame list after deletion."""
    savegame = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.delete(reverse("city:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert response.url == reverse("city:savegame-list")
