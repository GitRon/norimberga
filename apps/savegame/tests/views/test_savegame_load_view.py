import pytest
from django.urls import reverse

from apps.account.tests.factories import UserFactory
from apps.savegame.models import Savegame
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_savegame_load_view_requires_authentication(client):
    """Test SavegameLoadView requires user authentication."""
    savegame = SavegameFactory.create()
    response = client.post(reverse("savegame:savegame-load", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert reverse("account:login") in response.url


@pytest.mark.django_db
def test_savegame_load_view_sets_savegame_as_active(authenticated_client, user):
    """Test SavegameLoadView sets selected savegame as active."""
    savegame1 = SavegameFactory(user=user, is_active=True)
    savegame2 = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.post(reverse("savegame:savegame-load", kwargs={"pk": savegame2.pk}))

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

    response = authenticated_client.post(reverse("savegame:savegame-load", kwargs={"pk": savegame3.pk}))

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

    response = authenticated_client.post(reverse("savegame:savegame-load", kwargs={"pk": savegame.pk}))

    assert response.status_code == 200
    assert "HX-Redirect" in response
    assert response["HX-Redirect"] == reverse("city:landing-page")


@pytest.mark.django_db
def test_savegame_load_view_only_loads_own_savegame(authenticated_client, user):
    """Test SavegameLoadView only allows loading user's own savegames."""
    other_user = UserFactory(username="otheruser")
    other_savegame = SavegameFactory(user=other_user)

    with pytest.raises(Savegame.DoesNotExist):
        authenticated_client.post(reverse("savegame:savegame-load", kwargs={"pk": other_savegame.pk}))
