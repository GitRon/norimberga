import pytest
from django.urls import reverse

from apps.account.tests.factories import UserFactory
from apps.savegame.models import Savegame
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_savegame_list_view_requires_authentication(client):
    """Test SavegameListView requires user authentication."""
    response = client.get(reverse("savegame:savegame-list"))

    assert response.status_code == 302
    assert reverse("account:login") in response.url


@pytest.mark.django_db
def test_savegame_list_view_displays_user_savegames(authenticated_client, user):
    """Test SavegameListView displays only user's savegames."""
    savegame1 = SavegameFactory(user=user, city_name="User City 1")
    savegame2 = SavegameFactory(user=user, city_name="User City 2")
    other_user = UserFactory(username="otheruser")
    SavegameFactory(user=other_user, city_name="Other City")

    response = authenticated_client.get(reverse("savegame:savegame-list"))

    assert response.status_code == 200
    assert "savegame/savegame_list.html" in [t.name for t in response.templates]
    savegames = list(response.context["savegames"])
    assert len(savegames) == 2
    assert savegame1 in savegames
    assert savegame2 in savegames


@pytest.mark.django_db
def test_savegame_list_view_displays_no_savegames_message(authenticated_client, user):
    """Test SavegameListView displays message when user has no savegames."""
    # Delete any savegames
    Savegame.objects.filter(user=user).delete()

    response = authenticated_client.get(reverse("savegame:savegame-list"))

    assert response.status_code == 200
    savegames = list(response.context["savegames"])
    assert len(savegames) == 0


@pytest.mark.django_db
def test_savegame_list_view_orders_savegames_by_id_descending(authenticated_client, user):
    """Test SavegameListView orders savegames by ID descending."""
    savegame1 = SavegameFactory(user=user, city_name="First")
    savegame2 = SavegameFactory(user=user, city_name="Second")
    savegame3 = SavegameFactory(user=user, city_name="Third")

    response = authenticated_client.get(reverse("savegame:savegame-list"))

    savegames = list(response.context["savegames"])
    assert savegames[0] == savegame3
    assert savegames[1] == savegame2
    assert savegames[2] == savegame1
