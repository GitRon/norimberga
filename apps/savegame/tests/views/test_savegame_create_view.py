import pytest
from django.urls import reverse

from apps.savegame.models import Savegame
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_savegame_create_view_requires_authentication(client):
    """Test SavegameCreateView requires user authentication."""
    response = client.get(reverse("savegame:savegame-create"))

    assert response.status_code == 302
    assert reverse("account:login") in response.url


@pytest.mark.django_db
def test_savegame_create_view_creates_savegame_and_generates_map(authenticated_client, user):
    """Test SavegameCreateView creates savegame, generates map, and sets as active."""
    data = {
        "city_name": "New City",
    }

    response = authenticated_client.post(reverse("savegame:savegame-create"), data=data, follow=False)

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

    response = authenticated_client.post(reverse("savegame:savegame-create"), data=data, follow=False)

    assert response.status_code == 302

    # Verify existing savegames are now inactive
    existing1.refresh_from_db()
    existing2.refresh_from_db()
    assert existing1.is_active is False
    assert existing2.is_active is False

    # Verify new savegame is active
    new_savegame = Savegame.objects.get(user=user, city_name="New City")
    assert new_savegame.is_active is True


@pytest.mark.django_db
def test_savegame_create_view_generates_coat_of_arms(authenticated_client, user):
    """Test SavegameCreateView generates a coat of arms for the new savegame."""
    data = {
        "city_name": "New City",
    }

    response = authenticated_client.post(reverse("savegame:savegame-create"), data=data, follow=False)

    assert response.status_code == 302

    # Verify savegame was created with coat of arms
    savegame = Savegame.objects.get(user=user, city_name="New City")
    assert savegame.coat_of_arms
    assert savegame.coat_of_arms.name
    assert "coat_of_arms" in savegame.coat_of_arms.name
    assert savegame.coat_of_arms.name.endswith(".svg")
