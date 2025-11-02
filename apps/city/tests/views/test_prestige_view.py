import pytest
from django.urls import reverse

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_prestige_view_response(authenticated_client, user):
    """Test PrestigeView responds correctly."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert "city/prestige.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_prestige_view_with_savegame(authenticated_client, user):
    """Test PrestigeView includes prestige data when savegame exists."""
    SavegameFactory(user=user, is_active=True)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert "total_prestige" in response.context
    assert "prestige_breakdown" in response.context


@pytest.mark.django_db
def test_prestige_view_without_savegame(authenticated_client, user):
    """Test PrestigeView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_prestige_view_with_prestigious_buildings(authenticated_client, user):
    """Test PrestigeView calculates prestige correctly with buildings."""
    savegame = SavegameFactory(user=user, is_active=True)
    building1 = BuildingFactory.create(level=2, prestige=5)
    building2 = BuildingFactory.create(level=3, prestige=10)
    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert response.context["total_prestige"] == 15
    assert len(response.context["prestige_breakdown"]) == 2


@pytest.mark.django_db
def test_prestige_view_breakdown_structure(authenticated_client, user):
    """Test PrestigeView breakdown has correct structure."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory.create(name="Test Building", level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building, x=10, y=20)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    breakdown = response.context["prestige_breakdown"]
    assert len(breakdown) == 1
    assert breakdown[0]["building_name"] == "Test Building"
    assert breakdown[0]["level"] == 2
    assert breakdown[0]["prestige"] == 5
    assert breakdown[0]["x"] == 10
    assert breakdown[0]["y"] == 20


@pytest.mark.django_db
def test_prestige_view_no_prestige_buildings(authenticated_client, user):
    """Test PrestigeView with buildings that have no prestige."""
    savegame = SavegameFactory(user=user, is_active=True)
    building = BuildingFactory.create(level=1, prestige=0)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    assert response.context["total_prestige"] == 0
    assert len(response.context["prestige_breakdown"]) == 0


@pytest.mark.django_db
def test_prestige_view_breakdown_ordered_by_prestige(authenticated_client, user):
    """Test PrestigeView breakdown is ordered by prestige descending."""
    savegame = SavegameFactory(user=user, is_active=True)
    building1 = BuildingFactory.create(name="Low Prestige", level=2, prestige=3)
    building2 = BuildingFactory.create(name="High Prestige", level=3, prestige=10)
    building3 = BuildingFactory.create(name="Medium Prestige", level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)
    TileFactory.create(savegame=savegame, building=building3)

    response = authenticated_client.get(reverse("city:prestige"))

    assert response.status_code == 200
    breakdown = response.context["prestige_breakdown"]
    assert len(breakdown) == 3
    assert breakdown[0]["building_name"] == "High Prestige"
    assert breakdown[1]["building_name"] == "Medium Prestige"
    assert breakdown[2]["building_name"] == "Low Prestige"
