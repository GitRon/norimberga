import pytest

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory
from apps.thread.models import ActiveThread
from apps.thread.services.thread_checker import ThreadCheckerService
from apps.thread.tests.factories import ActiveThreadFactory, ThreadTypeFactory


@pytest.mark.django_db
def test_thread_checker_service_no_thread_types():
    """Test service returns empty list when no thread types are defined."""
    savegame = SavegameFactory.create()
    service = ThreadCheckerService(savegame=savegame)

    result = service.process()

    assert result == []


@pytest.mark.django_db
def test_thread_checker_service_activates_thread_when_condition_met():
    """Test service creates active thread when condition is met."""
    savegame = SavegameFactory.create(is_enclosed=True, current_year=1200)

    # Create prestige > defense scenario
    building = BuildingFactory.create(prestige=20, defense_value=5)
    TileFactory.create(savegame=savegame, building=building)

    # Create thread type
    thread_type = ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    assert len(result) == 1
    assert result[0].thread_type == thread_type
    assert result[0].savegame == savegame
    assert result[0].activated_at == 1200
    assert result[0].intensity == 15


@pytest.mark.django_db
def test_thread_checker_service_does_not_activate_when_condition_not_met():
    """Test service does not create active thread when condition is not met."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create defense > prestige scenario
    building = BuildingFactory.create(prestige=5, defense_value=20)
    TileFactory.create(savegame=savegame, building=building)

    # Create thread type
    ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    assert len(result) == 0
    assert ActiveThread.objects.filter(savegame=savegame).count() == 0


@pytest.mark.django_db
def test_thread_checker_service_deactivates_thread_when_condition_no_longer_met():
    """Test service removes active thread when condition is no longer met."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create thread type
    thread_type = ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create existing active thread
    ActiveThreadFactory.create(savegame=savegame, thread_type=thread_type, intensity=10)

    # Create defense > prestige scenario (condition not met)
    building = BuildingFactory.create(prestige=5, defense_value=20)
    TileFactory.create(savegame=savegame, building=building)

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    assert len(result) == 0
    assert ActiveThread.objects.filter(savegame=savegame).count() == 0


@pytest.mark.django_db
def test_thread_checker_service_updates_intensity_of_existing_thread():
    """Test service updates intensity when thread remains active but intensity changes."""
    savegame = SavegameFactory.create(is_enclosed=True, current_year=1200)

    # Create thread type
    thread_type = ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create existing active thread with intensity 10
    existing_thread = ActiveThreadFactory.create(
        savegame=savegame, thread_type=thread_type, intensity=10, activated_at=1150
    )

    # Create prestige > defense scenario with new intensity
    building = BuildingFactory.create(prestige=30, defense_value=5)
    TileFactory.create(savegame=savegame, building=building)

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    assert len(result) == 1
    assert result[0].id == existing_thread.id
    assert result[0].intensity == 25
    assert result[0].activated_at == 1150  # Original activation year preserved


@pytest.mark.django_db
def test_thread_checker_service_handles_multiple_thread_types():
    """Test service correctly handles multiple thread types."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create two thread types (only one will be active)
    thread_type1 = ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )
    thread_type2 = ThreadTypeFactory.create(
        name="Another Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create prestige > defense scenario
    building = BuildingFactory.create(prestige=20, defense_value=5)
    TileFactory.create(savegame=savegame, building=building)

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    # Both threads should be active since they use same condition
    assert len(result) == 2
    thread_types = {t.thread_type for t in result}
    assert thread_type1 in thread_types
    assert thread_type2 in thread_types


@pytest.mark.django_db
def test_thread_checker_service_handles_invalid_condition_class():
    """Test service gracefully handles invalid condition class path."""
    savegame = SavegameFactory.create()

    # Create thread type with invalid condition class
    ThreadTypeFactory.create(
        name="Invalid Thread",
        condition_class="apps.thread.conditions.nonexistent.InvalidThread",
    )

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    # Should not crash, just return empty list
    assert result == []


@pytest.mark.django_db
def test_thread_checker_service_handles_malformed_condition_class():
    """Test service gracefully handles malformed condition class string."""
    savegame = SavegameFactory.create()

    # Create thread type with malformed condition class
    ThreadTypeFactory.create(
        name="Malformed Thread",
        condition_class="this_is_not_valid",
    )

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    # Should not crash, just return empty list
    assert result == []


@pytest.mark.django_db
def test_thread_checker_service_only_affects_specific_savegame():
    """Test service only creates threads for the specified savegame."""
    savegame1 = SavegameFactory.create(is_enclosed=True)
    savegame2 = SavegameFactory.create(is_enclosed=True)

    # Create thread type
    thread_type = ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create prestige > defense only for savegame1
    building1 = BuildingFactory.create(prestige=20, defense_value=5)
    TileFactory.create(savegame=savegame1, building=building1)

    # Create defense > prestige for savegame2
    building2 = BuildingFactory.create(prestige=5, defense_value=20)
    TileFactory.create(savegame=savegame2, building=building2)

    service1 = ThreadCheckerService(savegame=savegame1)
    service2 = ThreadCheckerService(savegame=savegame2)

    result1 = service1.process()
    result2 = service2.process()

    # Only savegame1 should have active thread
    assert len(result1) == 1
    assert result1[0].thread_type == thread_type
    assert len(result2) == 0


@pytest.mark.django_db
def test_thread_checker_service_returns_all_active_threads():
    """Test service returns all active threads after processing."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create multiple thread types
    ThreadTypeFactory.create(
        name="Thread 1",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
        order=1,
    )
    ThreadTypeFactory.create(
        name="Thread 2",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
        order=2,
    )

    # Create prestige > defense scenario
    building = BuildingFactory.create(prestige=20, defense_value=5)
    TileFactory.create(savegame=savegame, building=building)

    service = ThreadCheckerService(savegame=savegame)
    result = service.process()

    assert len(result) == 2
    assert all(isinstance(t, ActiveThread) for t in result)


@pytest.mark.django_db
def test_thread_checker_service_preserves_unrelated_active_threads():
    """Test service preserves active threads from other savegames."""
    savegame1 = SavegameFactory.create(is_enclosed=True)
    savegame2 = SavegameFactory.create(is_enclosed=True)

    thread_type = ThreadTypeFactory.create(
        name="Prestige Defense Thread",
        condition_class="apps.thread.conditions.prestige_defense.PrestigeDefenseThread",
    )

    # Create active thread for savegame2
    other_thread = ActiveThreadFactory.create(savegame=savegame2, thread_type=thread_type)

    # Process savegame1 (no active threads)
    building = BuildingFactory.create(prestige=5, defense_value=20)
    TileFactory.create(savegame=savegame1, building=building)

    service = ThreadCheckerService(savegame=savegame1)
    service.process()

    # Other thread should still exist
    assert ActiveThread.objects.filter(id=other_thread.id).exists()
