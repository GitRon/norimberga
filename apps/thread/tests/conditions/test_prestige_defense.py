import pytest

from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory, TileFactory
from apps.savegame.tests.factories import SavegameFactory
from apps.thread.conditions.prestige_defense import PrestigeDefenseThread


@pytest.mark.django_db
def test_prestige_defense_thread_is_not_active_when_prestige_equals_defense():
    """Test thread is not active when prestige equals defense."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create building with both prestige and defense (same value)
    building = BuildingFactory.create(prestige=10, defense_value=10)
    TileFactory.create(savegame=savegame, building=building)

    condition = PrestigeDefenseThread(savegame=savegame)
    result = condition.is_active()

    assert result is False


@pytest.mark.django_db
def test_prestige_defense_thread_is_not_active_when_prestige_less_than_defense():
    """Test thread is not active when prestige is less than defense."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create building with more defense than prestige
    building = BuildingFactory.create(prestige=5, defense_value=15)
    TileFactory.create(savegame=savegame, building=building)

    condition = PrestigeDefenseThread(savegame=savegame)
    result = condition.is_active()

    assert result is False


@pytest.mark.django_db
def test_prestige_defense_thread_is_active_when_prestige_exceeds_defense():
    """Test thread is active when prestige exceeds defense."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create building with more prestige than defense
    building = BuildingFactory.create(prestige=20, defense_value=5)
    TileFactory.create(savegame=savegame, building=building)

    condition = PrestigeDefenseThread(savegame=savegame)
    result = condition.is_active()

    assert result is True


@pytest.mark.django_db
def test_prestige_defense_thread_is_active_with_no_defense():
    """Test thread is active when city has prestige but no defense."""
    savegame = SavegameFactory.create(is_enclosed=False)

    # Create building with prestige but no defense
    building = BuildingFactory.create(prestige=10, defense_value=0)
    TileFactory.create(savegame=savegame, building=building)

    condition = PrestigeDefenseThread(savegame=savegame)
    result = condition.is_active()

    assert result is True


@pytest.mark.django_db
def test_prestige_defense_thread_is_not_active_with_no_prestige():
    """Test thread is not active when city has no prestige."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create building with defense but no prestige
    building = BuildingFactory.create(prestige=0, defense_value=10)
    TileFactory.create(savegame=savegame, building=building)

    condition = PrestigeDefenseThread(savegame=savegame)
    result = condition.is_active()

    assert result is False


@pytest.mark.django_db
def test_prestige_defense_thread_intensity_calculation():
    """Test intensity is calculated as prestige minus defense."""
    savegame = SavegameFactory.create(is_enclosed=False)

    # Create buildings with prestige and defense
    building1 = BuildingFactory.create(prestige=15, defense_value=5)
    building2 = BuildingFactory.create(prestige=10, defense_value=5)

    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)

    condition = PrestigeDefenseThread(savegame=savegame)
    intensity = condition.get_intensity()

    # Prestige = 15 + 10 = 25
    # Defense = 0 (walls not actually enclosed, so defense is 0 regardless of defense_value)
    # Intensity should be 25 - 0 = 25
    assert intensity == 25


@pytest.mark.django_db
def test_prestige_defense_thread_intensity_zero_when_defense_higher():
    """Test intensity is zero when defense is higher than prestige."""
    savegame = SavegameFactory.create(is_enclosed=True)

    # Create building with more defense than prestige
    building = BuildingFactory.create(prestige=5, defense_value=20)
    TileFactory.create(savegame=savegame, building=building)

    condition = PrestigeDefenseThread(savegame=savegame)
    intensity = condition.get_intensity()

    # Intensity should be max(0, 5 - 20) = 0
    assert intensity == 0


@pytest.mark.django_db
def test_prestige_defense_thread_respects_wall_enclosure():
    """Test that defense calculation respects wall enclosure requirement."""
    savegame = SavegameFactory.create(is_enclosed=False)

    # Create wall building
    wall_type = BuildingTypeFactory.create(is_wall=True)
    wall_building = BuildingFactory.create(building_type=wall_type, defense_value=10)
    TileFactory.create(savegame=savegame, building=wall_building)

    # Create prestige building
    prestige_building = BuildingFactory.create(prestige=5, defense_value=0)
    TileFactory.create(savegame=savegame, building=prestige_building)

    condition = PrestigeDefenseThread(savegame=savegame)

    # Defense should be 0 because walls are not enclosed
    # Prestige is 5, so intensity should be 5 - 0 = 5
    intensity = condition.get_intensity()
    assert intensity == 5


@pytest.mark.django_db
def test_prestige_defense_thread_verbose_name():
    """Test thread condition has correct verbose name."""
    savegame = SavegameFactory.create()
    condition = PrestigeDefenseThread(savegame=savegame)

    assert condition.get_verbose_name() == "Prestige Exceeds Defense"


@pytest.mark.django_db
def test_prestige_defense_thread_multiple_buildings():
    """Test thread calculation with multiple buildings of different types."""
    savegame = SavegameFactory.create(is_enclosed=False)

    # Create multiple buildings
    building1 = BuildingFactory.create(prestige=10, defense_value=3)
    building2 = BuildingFactory.create(prestige=5, defense_value=2)
    building3 = BuildingFactory.create(prestige=8, defense_value=5)

    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)
    TileFactory.create(savegame=savegame, building=building3)

    condition = PrestigeDefenseThread(savegame=savegame)

    # Total prestige = 10 + 5 + 8 = 23
    # Total defense = 0 (walls not enclosed)
    # Thread should be active
    assert condition.is_active() is True
    assert condition.get_intensity() == 23
