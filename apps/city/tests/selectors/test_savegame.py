import pytest

from apps.city.models import Savegame
from apps.city.selectors.savegame import get_balance_data
from apps.city.tests.factories import BuildingFactory, SavegameFactory, TileFactory


@pytest.mark.django_db
def test_get_balance_data_with_buildings():
    """Test get_balance_data calculates balance correctly with buildings."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with taxes and maintenance costs
    building1 = BuildingFactory(taxes=20, maintenance_costs=5)
    building2 = BuildingFactory(taxes=30, maintenance_costs=8)
    building3 = BuildingFactory(taxes=15, maintenance_costs=3)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=building3)

    result = get_balance_data(savegame_id=1)

    assert result["savegame"] == savegame
    assert result["taxes"] == 65  # 20 + 30 + 15
    assert result["maintenance"] == 16  # 5 + 8 + 3
    assert result["balance"] == 49  # 65 - 16


@pytest.mark.django_db
def test_get_balance_data_no_buildings():
    """Test get_balance_data returns zero balance when no buildings exist."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create tiles without buildings
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=None)

    result = get_balance_data(savegame_id=1)

    assert result["savegame"] == savegame
    assert result["taxes"] == 0
    assert result["maintenance"] == 0
    assert result["balance"] == 0


@pytest.mark.django_db
def test_get_balance_data_empty_savegame():
    """Test get_balance_data returns zero balance for savegame with no tiles."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    result = get_balance_data(savegame_id=1)

    assert result["savegame"] == savegame
    assert result["taxes"] == 0
    assert result["maintenance"] == 0
    assert result["balance"] == 0


@pytest.mark.django_db
def test_get_balance_data_positive_balance():
    """Test get_balance_data returns positive balance when taxes exceed maintenance."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with higher taxes than maintenance
    building = BuildingFactory(taxes=50, maintenance_costs=10)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    assert result["balance"] == 40
    assert result["balance"] > 0


@pytest.mark.django_db
def test_get_balance_data_negative_balance():
    """Test get_balance_data returns negative balance when maintenance exceeds taxes."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with higher maintenance than taxes
    building = BuildingFactory(taxes=10, maintenance_costs=50)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    assert result["balance"] == -40
    assert result["balance"] < 0


@pytest.mark.django_db
def test_get_balance_data_mixed_tiles():
    """Test get_balance_data with mix of tiles with and without buildings."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create mix of tiles
    building1 = BuildingFactory(taxes=25, maintenance_costs=10)
    building2 = BuildingFactory(taxes=35, maintenance_costs=15)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=None)

    result = get_balance_data(savegame_id=1)

    assert result["taxes"] == 60  # 25 + 35
    assert result["maintenance"] == 25  # 10 + 15
    assert result["balance"] == 35  # 60 - 25


@pytest.mark.django_db
def test_get_balance_data_zero_values():
    """Test get_balance_data handles buildings with zero taxes and maintenance."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with zero values
    building = BuildingFactory(taxes=0, maintenance_costs=0)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    assert result["taxes"] == 0
    assert result["maintenance"] == 0
    assert result["balance"] == 0


@pytest.mark.django_db
def test_get_balance_data_only_taxes():
    """Test get_balance_data with buildings that only have taxes."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with taxes but no maintenance
    building = BuildingFactory(taxes=40, maintenance_costs=0)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    assert result["taxes"] == 40
    assert result["maintenance"] == 0
    assert result["balance"] == 40


@pytest.mark.django_db
def test_get_balance_data_only_maintenance():
    """Test get_balance_data with buildings that only have maintenance costs."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with maintenance but no taxes
    building = BuildingFactory(taxes=0, maintenance_costs=30)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    assert result["taxes"] == 0
    assert result["maintenance"] == 30
    assert result["balance"] == -30


@pytest.mark.django_db
def test_get_balance_data_multiple_savegames():
    """Test get_balance_data only returns data for specified savegame."""
    # Clear any existing savegames
    Savegame.objects.filter(id__in=[1, 2]).delete()

    savegame1 = SavegameFactory(id=1)
    savegame2 = SavegameFactory(id=2)

    # Create buildings for savegame1
    building1 = BuildingFactory(taxes=20, maintenance_costs=10)
    TileFactory(savegame=savegame1, building=building1)

    # Create buildings for savegame2
    building2 = BuildingFactory(taxes=50, maintenance_costs=25)
    TileFactory(savegame=savegame2, building=building2)

    # Get data for savegame1
    result = get_balance_data(savegame_id=1)

    assert result["savegame"] == savegame1
    assert result["taxes"] == 20
    assert result["maintenance"] == 10
    assert result["balance"] == 10


@pytest.mark.django_db
def test_get_balance_data_returns_dict_with_all_keys():
    """Test get_balance_data returns dictionary with all expected keys."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)
    building = BuildingFactory()
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    # Verify all expected keys are present
    assert "savegame" in result
    assert "taxes" in result
    assert "maintenance" in result
    assert "balance" in result

    # Verify types
    assert isinstance(result["savegame"], type(savegame))
    assert isinstance(result["taxes"], int)
    assert isinstance(result["maintenance"], int)
    assert isinstance(result["balance"], int)


@pytest.mark.django_db
def test_get_balance_data_large_numbers():
    """Test get_balance_data handles larger numbers correctly."""
    # Clear any existing savegame with id=1
    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create multiple buildings with various values
    for _ in range(10):
        building = BuildingFactory(taxes=100, maintenance_costs=75)
        TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame_id=1)

    assert result["taxes"] == 1000  # 100 * 10
    assert result["maintenance"] == 750  # 75 * 10
    assert result["balance"] == 250  # 1000 - 750
