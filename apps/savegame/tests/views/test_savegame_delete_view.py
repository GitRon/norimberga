from http import HTTPStatus

import pytest
from django.urls import reverse

from apps.account.tests.factories import UserFactory
from apps.savegame.models import Savegame
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_savegame_delete_view_requires_authentication(client):
    """Test SavegameDeleteView requires user authentication."""
    savegame = SavegameFactory.create()
    response = client.delete(reverse("savegame:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert reverse("account:login") in response.url


@pytest.mark.django_db
def test_savegame_delete_view_deletes_inactive_savegame(authenticated_client, user):
    """Test SavegameDeleteView deletes inactive savegame."""
    savegame = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.delete(reverse("savegame:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert not Savegame.objects.filter(pk=savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_cannot_delete_active_savegame(authenticated_client, user):
    """Test SavegameDeleteView cannot delete active savegame."""
    savegame = SavegameFactory(user=user, is_active=True)

    response = authenticated_client.delete(reverse("savegame:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 404
    assert Savegame.objects.filter(pk=savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_cannot_delete_other_users_savegame(authenticated_client, user):
    """Test SavegameDeleteView cannot delete other user's savegame."""
    other_user = UserFactory(username="otheruser")
    other_savegame = SavegameFactory(user=other_user, is_active=False)

    response = authenticated_client.delete(reverse("savegame:savegame-delete", kwargs={"pk": other_savegame.pk}))

    assert response.status_code == 404
    assert Savegame.objects.filter(pk=other_savegame.pk).exists()


@pytest.mark.django_db
def test_savegame_delete_view_redirects_to_savegame_list(authenticated_client, user):
    """Test SavegameDeleteView redirects to savegame list after deletion."""
    savegame = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.delete(reverse("savegame:savegame-delete", kwargs={"pk": savegame.pk}))

    assert response.status_code == 302
    assert response.url == reverse("savegame:savegame-list")


@pytest.mark.django_db
def test_savegame_delete_view_returns_ok_for_htmx_request(authenticated_client, user):
    """Test SavegameDeleteView returns 200 OK for HTMX requests."""
    savegame = SavegameFactory(user=user, is_active=False)

    response = authenticated_client.delete(
        reverse("savegame:savegame-delete", kwargs={"pk": savegame.pk}), HTTP_HX_REQUEST="true"
    )

    assert response.status_code == HTTPStatus.OK
    assert not Savegame.objects.filter(pk=savegame.pk).exists()
