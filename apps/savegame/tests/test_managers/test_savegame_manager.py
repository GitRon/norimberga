import pytest

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.savegame.managers.savegame import SavegameManager
from apps.savegame.tests.factories import SavegameFactory


def test_savegame_manager_from_queryset():
    """Test SavegameManager is created from SavegameQuerySet."""
    manager = SavegameManager()

    # Should have manager methods
    assert hasattr(manager, "aggregate_taxes")
    assert hasattr(manager, "aggregate_maintenance_costs")


@pytest.mark.django_db
def test_savegame_manager_aggregate_taxes_with_buildings():
    """Test aggregate_taxes returns sum of taxes from all buildings."""
    savegame = SavegameFactory()

    # Create tiles with buildings that have taxes
    building1 = BuildingFactory(taxes=10)
    building2 = BuildingFactory(taxes=25)
    building3 = BuildingFactory(taxes=15)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=building3)

    result = SavegameManager().aggregate_taxes(savegame=savegame)

    assert result == 50  # 10 + 25 + 15


@pytest.mark.django_db
def test_savegame_manager_aggregate_taxes_no_buildings():
    """Test aggregate_taxes returns 0 when no buildings exist."""
    savegame = SavegameFactory()

    # Create tiles without buildings
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=None)

    result = SavegameManager().aggregate_taxes(savegame=savegame)

    # Should return 0, not None
    assert result == 0


@pytest.mark.django_db
def test_savegame_manager_aggregate_taxes_empty_savegame():
    """Test aggregate_taxes returns 0 for savegame with no tiles."""
    savegame = SavegameFactory()

    result = SavegameManager().aggregate_taxes(savegame=savegame)

    # Should return 0, not None
    assert result == 0


@pytest.mark.django_db
def test_savegame_manager_aggregate_taxes_zero_taxes():
    """Test aggregate_taxes handles buildings with zero taxes."""
    savegame = SavegameFactory()

    # Create buildings with zero taxes
    building1 = BuildingFactory(taxes=0)
    building2 = BuildingFactory(taxes=0)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)

    result = SavegameManager().aggregate_taxes(savegame=savegame)

    assert result == 0


@pytest.mark.django_db
def test_savegame_manager_aggregate_taxes_mixed():
    """Test aggregate_taxes with mix of buildings and empty tiles."""
    savegame = SavegameFactory()

    # Create tiles with and without buildings
    building1 = BuildingFactory(taxes=20)
    building2 = BuildingFactory(taxes=30)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=None)

    result = SavegameManager().aggregate_taxes(savegame=savegame)

    assert result == 50  # 20 + 30


@pytest.mark.django_db
def test_savegame_manager_aggregate_maintenance_costs_with_buildings():
    """Test aggregate_maintenance_costs returns sum of maintenance costs."""
    savegame = SavegameFactory()

    # Create tiles with buildings that have maintenance costs
    building1 = BuildingFactory(maintenance_costs=5)
    building2 = BuildingFactory(maintenance_costs=8)
    building3 = BuildingFactory(maintenance_costs=12)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=building3)

    result = SavegameManager().aggregate_maintenance_costs(savegame=savegame)

    assert result == 25  # 5 + 8 + 12


@pytest.mark.django_db
def test_savegame_manager_aggregate_maintenance_costs_no_buildings():
    """Test aggregate_maintenance_costs returns 0 when no buildings exist."""
    savegame = SavegameFactory()

    # Create tiles without buildings
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=None)

    result = SavegameManager().aggregate_maintenance_costs(savegame=savegame)

    # Should return 0, not None
    assert result == 0


@pytest.mark.django_db
def test_savegame_manager_aggregate_maintenance_costs_empty_savegame():
    """Test aggregate_maintenance_costs returns 0 for savegame with no tiles."""
    savegame = SavegameFactory()

    result = SavegameManager().aggregate_maintenance_costs(savegame=savegame)

    # Should return 0, not None
    assert result == 0


@pytest.mark.django_db
def test_savegame_manager_aggregate_maintenance_costs_zero_costs():
    """Test aggregate_maintenance_costs handles buildings with zero costs."""
    savegame = SavegameFactory()

    # Create buildings with zero maintenance costs
    building1 = BuildingFactory(maintenance_costs=0)
    building2 = BuildingFactory(maintenance_costs=0)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)

    result = SavegameManager().aggregate_maintenance_costs(savegame=savegame)

    assert result == 0


@pytest.mark.django_db
def test_savegame_manager_aggregate_maintenance_costs_mixed():
    """Test aggregate_maintenance_costs with mix of buildings and empty tiles."""
    savegame = SavegameFactory()

    # Create tiles with and without buildings
    building1 = BuildingFactory(maintenance_costs=7)
    building2 = BuildingFactory(maintenance_costs=13)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=None)

    result = SavegameManager().aggregate_maintenance_costs(savegame=savegame)

    assert result == 20  # 7 + 13


@pytest.mark.django_db
def test_savegame_manager_aggregate_multiple_savegames():
    """Test aggregate methods only count buildings from specified savegame."""
    savegame1 = SavegameFactory()
    savegame2 = SavegameFactory()

    # Create buildings for savegame1
    building1 = BuildingFactory(taxes=10, maintenance_costs=5)
    building2 = BuildingFactory(taxes=20, maintenance_costs=8)

    # Create buildings for savegame2
    building3 = BuildingFactory(taxes=30, maintenance_costs=12)

    TileFactory(savegame=savegame1, building=building1)
    TileFactory(savegame=savegame1, building=building2)
    TileFactory(savegame=savegame2, building=building3)

    # Test savegame1
    taxes1 = SavegameManager().aggregate_taxes(savegame=savegame1)
    maintenance1 = SavegameManager().aggregate_maintenance_costs(savegame=savegame1)

    assert taxes1 == 30  # 10 + 20
    assert maintenance1 == 13  # 5 + 8

    # Test savegame2
    taxes2 = SavegameManager().aggregate_taxes(savegame=savegame2)
    maintenance2 = SavegameManager().aggregate_maintenance_costs(savegame=savegame2)

    assert taxes2 == 30
    assert maintenance2 == 12


@pytest.mark.django_db
def test_savegame_manager_integration():
    """Test SavegameManager works with actual model queries."""
    from apps.savegame.models import Savegame

    savegame = SavegameFactory()

    building = BuildingFactory(taxes=15, maintenance_costs=7)
    TileFactory(savegame=savegame, building=building)

    # Test manager methods work on actual model
    taxes = Savegame.objects.aggregate_taxes(savegame=savegame)
    maintenance = Savegame.objects.aggregate_maintenance_costs(savegame=savegame)

    assert taxes == 15
    assert maintenance == 7
