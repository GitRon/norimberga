import pytest
from django.urls import reverse

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory
from apps.thread.tests.factories import ThreadTypeFactory


@pytest.mark.django_db
def test_threads_view_response(authenticated_client, user):
    """Test ThreadsView responds correctly."""
    SavegameFactory.create(user=user, is_active=True)

    response = authenticated_client.get(reverse("thread:threads"))

    assert response.status_code == 200
    assert "thread/threads.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_threads_view_without_savegame(authenticated_client, user):
    """Test ThreadsView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("thread:threads"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_threads_view_includes_defense_data(authenticated_client, user):
    """Test ThreadsView includes defense breakdown in context."""
    SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    response = authenticated_client.get(reverse("thread:threads"))

    assert response.status_code == 200
    assert "breakdown" in response.context
    assert hasattr(response.context["breakdown"], "is_enclosed")
    assert hasattr(response.context["breakdown"], "base_defense")


@pytest.mark.django_db
def test_threads_view_includes_prestige_data(authenticated_client, user):
    """Test ThreadsView includes prestige data in context."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    building = BuildingFactory.create(prestige=10)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:threads"))

    assert response.status_code == 200
    assert "total_prestige" in response.context
    assert "prestige_breakdown" in response.context
    assert response.context["total_prestige"] == 10


@pytest.mark.django_db
def test_threads_view_includes_active_threads(authenticated_client, user):
    """Test ThreadsView includes active threads in context."""
    savegame = SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    # Create thread type with prestige-defense condition
    ThreadTypeFactory.create(condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread")

    # Create scenario where prestige > defense to activate thread
    building = BuildingFactory.create(prestige=20, defense_value=0)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:threads"))

    assert response.status_code == 200
    assert "active_threads" in response.context
    assert len(response.context["active_threads"]) == 1


@pytest.mark.django_db
def test_threads_view_runs_thread_checker(authenticated_client, user):
    """Test ThreadsView runs thread checker service on load."""
    savegame = SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    # Create thread type
    ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create prestige > defense scenario
    building = BuildingFactory.create(prestige=20, defense_value=5)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:threads"))

    assert response.status_code == 200
    # Thread checker should have activated the thread
    assert len(response.context["active_threads"]) == 1


@pytest.mark.django_db
def test_defense_tab_view_response(authenticated_client, user):
    """Test DefenseTabView responds correctly."""
    SavegameFactory.create(user=user, is_active=True)

    response = authenticated_client.get(reverse("thread:defense-tab"))

    assert response.status_code == 200
    assert "thread/partials/_defense_tab.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_defense_tab_view_includes_defense_data(authenticated_client, user):
    """Test DefenseTabView includes defense breakdown in context."""
    SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    response = authenticated_client.get(reverse("thread:defense-tab"))

    assert response.status_code == 200
    assert "breakdown" in response.context


@pytest.mark.django_db
def test_defense_tab_view_without_savegame(authenticated_client, user):
    """Test DefenseTabView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("thread:defense-tab"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_prestige_tab_view_response(authenticated_client, user):
    """Test PrestigeTabView responds correctly."""
    SavegameFactory.create(user=user, is_active=True)

    response = authenticated_client.get(reverse("thread:prestige-tab"))

    assert response.status_code == 200
    assert "thread/partials/_prestige_tab.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_prestige_tab_view_includes_prestige_data(authenticated_client, user):
    """Test PrestigeTabView includes prestige data in context."""
    savegame = SavegameFactory.create(user=user, is_active=True)
    building = BuildingFactory.create(prestige=15)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:prestige-tab"))

    assert response.status_code == 200
    assert "total_prestige" in response.context
    assert "prestige_breakdown" in response.context
    assert response.context["total_prestige"] == 15


@pytest.mark.django_db
def test_prestige_tab_view_without_savegame(authenticated_client, user):
    """Test PrestigeTabView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("thread:prestige-tab"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_threads_tab_view_response(authenticated_client, user):
    """Test ThreadsTabView responds correctly."""
    SavegameFactory.create(user=user, is_active=True)

    response = authenticated_client.get(reverse("thread:threads-tab"))

    assert response.status_code == 200
    assert "thread/partials/_threads_tab.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_threads_tab_view_includes_active_threads(authenticated_client, user):
    """Test ThreadsTabView includes active threads in context."""
    savegame = SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    # Create thread type with prestige-defense condition
    ThreadTypeFactory.create(condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread")

    # Create scenario where prestige > defense to activate thread
    building = BuildingFactory.create(prestige=25, defense_value=0)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:threads-tab"))

    assert response.status_code == 200
    assert "active_threads" in response.context
    assert len(response.context["active_threads"]) == 1


@pytest.mark.django_db
def test_threads_tab_view_runs_thread_checker(authenticated_client, user):
    """Test ThreadsTabView runs thread checker service."""
    savegame = SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    # Create thread type
    ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create prestige > defense scenario
    building = BuildingFactory.create(prestige=30, defense_value=10)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:threads-tab"))

    assert response.status_code == 200
    # Thread checker should have activated the thread
    assert len(response.context["active_threads"]) == 1
    assert response.context["active_threads"][0].intensity == 20


@pytest.mark.django_db
def test_threads_tab_view_without_savegame(authenticated_client, user):
    """Test ThreadsTabView redirects when no active savegame exists."""
    response = authenticated_client.get(reverse("thread:threads-tab"))

    assert response.status_code == 302
    assert response.url == "/savegame/savegames/"


@pytest.mark.django_db
def test_threads_tab_view_with_multiple_active_threads(authenticated_client, user):
    """Test ThreadsTabView displays multiple active threads correctly."""
    savegame = SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    # Create two thread types with prestige-defense condition
    ThreadTypeFactory.create(
        name="Thread 1",
        order=1,
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )
    ThreadTypeFactory.create(
        name="Thread 2",
        order=2,
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create scenario where prestige > defense to activate both threads
    building = BuildingFactory.create(prestige=50, defense_value=0)
    TileFactory.create(savegame=savegame, building=building)

    response = authenticated_client.get(reverse("thread:threads-tab"))

    assert response.status_code == 200
    assert len(response.context["active_threads"]) == 2


@pytest.mark.django_db
def test_threads_tab_view_with_no_active_threads(authenticated_client, user):
    """Test ThreadsTabView handles no active threads gracefully."""
    SavegameFactory.create(user=user, is_active=True, is_enclosed=True)

    response = authenticated_client.get(reverse("thread:threads-tab"))

    assert response.status_code == 200
    assert "active_threads" in response.context
    assert len(response.context["active_threads"]) == 0
