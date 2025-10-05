import pytest
from django.urls import reverse

from apps.city.models import Savegame
from apps.city.tests.factories import SavegameFactory, UserFactory


# SavegameListView Tests
@pytest.mark.django_db
def test_savegame_list_view_requires_authentication(client):
    """Test SavegameListView requires user authentication."""
    response = client.get(reverse("city:savegame-list"))

    assert response.status_code == 302
    assert reverse("account:login") in response.url


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
def test_savegame_list_view_displays_no_savegames_message(authenticated_client, user):
    """Test SavegameListView displays message when user has no savegames."""
    # Delete any savegames
    Savegame.objects.filter(user=user).delete()

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
    assert reverse("account:login") in response.url


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
    assert reverse("account:login") in response.url


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


@pytest.mark.django_db
def test_savegame_delete_view_returns_ok_for_htmx_request(authenticated_client, user):
    """Test SavegameDeleteView returns 200 OK for HTMX requests."""
    from http import HTTPStatus

    savegame = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.delete(
        reverse("city:savegame-delete", kwargs={"pk": savegame.pk}), HTTP_HX_REQUEST="true"
    )

    assert response.status_code == HTTPStatus.OK
    assert not Savegame.objects.filter(pk=savegame.pk).exists()


# SavegameCreateView Tests
@pytest.mark.django_db
def test_savegame_create_view_requires_authentication(client):
    """Test SavegameCreateView requires user authentication."""
    response = client.get(reverse("city:savegame-create"))

    assert response.status_code == 302
    assert reverse("account:login") in response.url


@pytest.mark.django_db
def test_savegame_create_view_creates_savegame_and_generates_map(authenticated_client, user):
    """Test SavegameCreateView creates savegame, generates map, and sets as active."""
    data = {
        "city_name": "New City",
    }

    response = authenticated_client.post(reverse("city:savegame-create"), data=data, follow=False)

    assert response.status_code == 302
    assert response.url == reverse("city:landing-page")

    # Verify savegame was created
    savegame = Savegame.objects.get(user=user, city_name="New City")
    assert savegame.is_active is True

    # Verify other savegames were deactivated
    other_savegames = Savegame.objects.filter(user=user).exclude(pk=savegame.pk)
    for sg in other_savegames:
        assert sg.is_active is False


@pytest.mark.django_db
def test_savegame_create_view_deactivates_existing_savegames(authenticated_client, user):
    """Test SavegameCreateView deactivates existing active savegames."""
    # Create existing active savegames
    existing1 = SavegameFactory(user=user, is_active=True)
    existing2 = SavegameFactory(user=user, is_active=True)

    data = {
        "city_name": "New City",
    }

    response = authenticated_client.post(reverse("city:savegame-create"), data=data, follow=False)

    assert response.status_code == 302

    # Verify existing savegames are now inactive
    existing1.refresh_from_db()
    existing2.refresh_from_db()
    assert existing1.is_active is False
    assert existing2.is_active is False

    # Verify new savegame is active
    new_savegame = Savegame.objects.get(user=user, city_name="New City")
    assert new_savegame.is_active is True


# LandingPageView Tests
@pytest.mark.django_db
def test_landing_page_view_redirects_to_savegame_list_when_no_active_savegame(authenticated_client, user):
    """Test LandingPageView redirects to savegame list when user has no active savegame."""
    Savegame.objects.filter(user=user).update(is_active=False)

    response = authenticated_client.get(reverse("city:landing-page"), follow=False)

    assert response.status_code == 302
    assert response.url == reverse("city:savegame-list")


@pytest.mark.django_db
def test_landing_page_view_displays_when_user_has_active_savegame(authenticated_client, user):
    """Test LandingPageView displays when user has an active savegame."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:landing-page"))

    assert response.status_code == 200
    assert "city/landing_page.html" in [t.name for t in response.templates]
