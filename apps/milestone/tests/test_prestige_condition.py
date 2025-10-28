import pytest

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.milestone.conditions.prestige import MinPrestigeCondition
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_min_prestige_condition_met():
    """Test that condition is valid when prestige meets the minimum."""
    savegame = SavegameFactory.create()
    building = BuildingFactory.create(level=2, prestige=10)
    TileFactory.create(savegame=savegame, building=building)

    condition = MinPrestigeCondition(savegame=savegame, value=10)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_prestige_condition_exceeded():
    """Test that condition is valid when prestige exceeds the minimum."""
    savegame = SavegameFactory.create()
    building1 = BuildingFactory.create(level=2, prestige=5)
    building2 = BuildingFactory.create(level=3, prestige=10)
    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)

    condition = MinPrestigeCondition(savegame=savegame, value=10)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_prestige_condition_not_met():
    """Test that condition is invalid when prestige is below the minimum."""
    savegame = SavegameFactory.create()
    building = BuildingFactory.create(level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building)

    condition = MinPrestigeCondition(savegame=savegame, value=10)

    assert condition.is_valid() is False


@pytest.mark.django_db
def test_min_prestige_condition_no_prestige():
    """Test that condition is invalid when there is no prestige."""
    savegame = SavegameFactory.create()

    condition = MinPrestigeCondition(savegame=savegame, value=1)

    assert condition.is_valid() is False


@pytest.mark.django_db
def test_min_prestige_condition_zero_value():
    """Test that condition is valid when minimum is zero and there is no prestige."""
    savegame = SavegameFactory.create()

    condition = MinPrestigeCondition(savegame=savegame, value=0)

    assert condition.is_valid() is True


@pytest.mark.django_db
def test_min_prestige_condition_verbose_name():
    """Test that the condition has the correct verbose name."""
    savegame = SavegameFactory.create()
    condition = MinPrestigeCondition(savegame=savegame, value=10)

    assert condition.get_verbose_name() == "Minimum Prestige"
