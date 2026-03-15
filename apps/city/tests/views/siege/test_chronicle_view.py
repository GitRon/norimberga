import pytest
from django.urls import reverse

from apps.savegame.tests.factories import SavegameFactory, SiegeChronicleFactory


@pytest.mark.django_db
def test_siege_chronicle_view_requires_savegame(authenticated_client, user):
    """Test view redirects when no active savegame."""
    response = authenticated_client.get(reverse("city:siege-chronicle"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_siege_chronicle_view_renders_with_savegame(authenticated_client, user):
    """Test view renders successfully with active savegame."""
    SavegameFactory.create(user=user, is_active=True)
    response = authenticated_client.get(reverse("city:siege-chronicle"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_siege_chronicle_view_shows_chronicles(authenticated_client, user):
    """Test view includes siege chronicles in context."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    SiegeChronicleFactory.create(savegame=savegame, year=1155, report_text="First siege.")
    SiegeChronicleFactory.create(savegame=savegame, year=1160, report_text="Second siege.")

    response = authenticated_client.get(reverse("city:siege-chronicle"))

    assert response.status_code == 200
    chronicles = response.context["chronicles"]
    assert chronicles.count() == 2


@pytest.mark.django_db
def test_siege_chronicle_view_empty_chronicles(authenticated_client, user):
    """Test view handles no chronicles gracefully."""
    SavegameFactory.create(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:siege-chronicle"))

    assert response.status_code == 200
    chronicles = response.context["chronicles"]
    assert chronicles.count() == 0


@pytest.mark.django_db
def test_siege_chronicle_view_chronicles_ordered_by_year(authenticated_client, user):
    """Test chronicles are returned ordered by year ascending."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    SiegeChronicleFactory.create(savegame=savegame, year=1200)
    SiegeChronicleFactory.create(savegame=savegame, year=1155)
    SiegeChronicleFactory.create(savegame=savegame, year=1175)

    response = authenticated_client.get(reverse("city:siege-chronicle"))

    years = list(response.context["chronicles"].values_list("year", flat=True))
    assert years == [1155, 1175, 1200]


@pytest.mark.django_db
def test_siege_chronicle_view_only_shows_own_chronicles(authenticated_client, user):
    """Test view only shows chronicles for the active savegame."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    other_savegame = SavegameFactory.create(is_active=False)

    SiegeChronicleFactory.create(savegame=savegame, year=1155)
    SiegeChronicleFactory.create(savegame=other_savegame, year=1160)

    response = authenticated_client.get(reverse("city:siege-chronicle"))

    chronicles = response.context["chronicles"]
    assert chronicles.count() == 1
    assert chronicles.first().year == 1155
