import pytest

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.savegame.selectors.savegame import get_balance_data
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_get_balance_data_with_buildings():
    """Test get_balance_data calculates balance correctly with buildings."""
    savegame = SavegameFactory()

    # Create buildings with taxes and maintenance costs
    building1 = BuildingFactory(taxes=20, maintenance_costs=5)
    building2 = BuildingFactory(taxes=30, maintenance_costs=8)
    building3 = BuildingFactory(taxes=15, maintenance_costs=3)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=building3)

    result = get_balance_data(savegame=savegame)

    assert result["savegame"] == savegame
    assert result["taxes"] == 65  # 20 + 30 + 15
    assert result["maintenance"] == 16  # 5 + 8 + 3
    assert result["balance"] == 49  # 65 - 16


@pytest.mark.django_db
def test_get_balance_data_no_buildings():
    """Test get_balance_data returns zero balance when no buildings exist."""
    savegame = SavegameFactory()

    # Create tiles without buildings
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=None)

    result = get_balance_data(savegame=savegame)

    assert result["savegame"] == savegame
    assert result["taxes"] == 0
    assert result["maintenance"] == 0
    assert result["balance"] == 0


@pytest.mark.django_db
def test_get_balance_data_empty_savegame():
    """Test get_balance_data returns zero balance for savegame with no tiles."""
    savegame = SavegameFactory()

    result = get_balance_data(savegame=savegame)

    assert result["savegame"] == savegame
    assert result["taxes"] == 0
    assert result["maintenance"] == 0
    assert result["balance"] == 0


@pytest.mark.django_db
def test_get_balance_data_positive_balance():
    """Test get_balance_data returns positive balance when taxes exceed maintenance."""
    savegame = SavegameFactory()

    # Create buildings with higher taxes than maintenance
    building = BuildingFactory(taxes=50, maintenance_costs=10)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    assert result["balance"] == 40
    assert result["balance"] > 0


@pytest.mark.django_db
def test_get_balance_data_negative_balance():
    """Test get_balance_data returns negative balance when maintenance exceeds taxes."""
    savegame = SavegameFactory()

    # Create buildings with higher maintenance than taxes
    building = BuildingFactory(taxes=10, maintenance_costs=50)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    assert result["balance"] == -40
    assert result["balance"] < 0


@pytest.mark.django_db
def test_get_balance_data_mixed_tiles():
    """Test get_balance_data with mix of tiles with and without buildings."""
    savegame = SavegameFactory()

    # Create mix of tiles
    building1 = BuildingFactory(taxes=25, maintenance_costs=10)
    building2 = BuildingFactory(taxes=35, maintenance_costs=15)

    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=None)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=None)

    result = get_balance_data(savegame=savegame)

    assert result["taxes"] == 60  # 25 + 35
    assert result["maintenance"] == 25  # 10 + 15
    assert result["balance"] == 35  # 60 - 25


@pytest.mark.django_db
def test_get_balance_data_zero_values():
    """Test get_balance_data handles buildings with zero taxes and maintenance."""
    savegame = SavegameFactory()

    # Create buildings with zero values
    building = BuildingFactory(taxes=0, maintenance_costs=0)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    assert result["taxes"] == 0
    assert result["maintenance"] == 0
    assert result["balance"] == 0


@pytest.mark.django_db
def test_get_balance_data_only_taxes():
    """Test get_balance_data with buildings that only have taxes."""
    savegame = SavegameFactory()

    # Create buildings with taxes but no maintenance
    building = BuildingFactory(taxes=40, maintenance_costs=0)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    assert result["taxes"] == 40
    assert result["maintenance"] == 0
    assert result["balance"] == 40


@pytest.mark.django_db
def test_get_balance_data_only_maintenance():
    """Test get_balance_data with buildings that only have maintenance costs."""
    savegame = SavegameFactory()

    # Create buildings with maintenance but no taxes
    building = BuildingFactory(taxes=0, maintenance_costs=30)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    assert result["taxes"] == 0
    assert result["maintenance"] == 30
    assert result["balance"] == -30


@pytest.mark.django_db
def test_get_balance_data_multiple_savegames():
    """Test get_balance_data only returns data for specified savegame."""
    savegame1 = SavegameFactory()
    savegame2 = SavegameFactory()

    # Create buildings for savegame1
    building1 = BuildingFactory(taxes=20, maintenance_costs=10)
    TileFactory(savegame=savegame1, building=building1)

    # Create buildings for savegame2
    building2 = BuildingFactory(taxes=50, maintenance_costs=25)
    TileFactory(savegame=savegame2, building=building2)

    # Get data for savegame1
    result = get_balance_data(savegame=savegame1)

    assert result["savegame"] == savegame1
    assert result["taxes"] == 20
    assert result["maintenance"] == 10
    assert result["balance"] == 10


@pytest.mark.django_db
def test_get_balance_data_returns_dict_with_all_keys():
    """Test get_balance_data returns dictionary with all expected keys."""
    savegame = SavegameFactory()
    building = BuildingFactory()
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    # Verify all expected keys are present
    assert "savegame" in result
    assert "taxes" in result
    assert "maintenance" in result
    assert "balance" in result
    assert "tax_by_building_type" in result
    assert "maintenance_by_building_type" in result

    # Verify types
    assert isinstance(result["savegame"], type(savegame))
    assert isinstance(result["taxes"], int)
    assert isinstance(result["maintenance"], int)
    assert isinstance(result["balance"], int)
    assert isinstance(result["tax_by_building_type"], dict)
    assert isinstance(result["maintenance_by_building_type"], dict)


@pytest.mark.django_db
def test_get_balance_data_large_numbers():
    """Test get_balance_data handles larger numbers correctly."""
    savegame = SavegameFactory()

    # Create multiple buildings with various values
    buildings = BuildingFactory.create_batch(10, taxes=100, maintenance_costs=75)
    for i, building in enumerate(buildings):
        TileFactory(savegame=savegame, building=building, x=i, y=0)

    result = get_balance_data(savegame=savegame)

    assert result["taxes"] == 1000  # 100 * 10
    assert result["maintenance"] == 750  # 75 * 10
    assert result["balance"] == 250  # 1000 - 750


@pytest.mark.django_db
def test_get_balance_data_tax_grouping_by_building_type():
    """Test tax breakdown is grouped by building type and then by building."""
    savegame = SavegameFactory()

    # Create building types
    from apps.city.tests.factories import BuildingTypeFactory

    house_type = BuildingTypeFactory(name="House")
    workshop_type = BuildingTypeFactory(name="Workshop")

    # Create buildings with same type
    house1 = BuildingFactory(name="Small House", building_type=house_type, level=1, taxes=10, maintenance_costs=0)
    house2 = BuildingFactory(name="Large House", building_type=house_type, level=2, taxes=20, maintenance_costs=0)

    # Create workshop
    workshop1 = BuildingFactory(name="Blacksmith", building_type=workshop_type, level=1, taxes=15, maintenance_costs=0)

    # Place buildings on tiles
    TileFactory(savegame=savegame, building=house1)
    TileFactory(savegame=savegame, building=house1)  # 2x Small House
    TileFactory(savegame=savegame, building=house2)  # 1x Large House
    TileFactory(savegame=savegame, building=workshop1)  # 1x Blacksmith

    result = get_balance_data(savegame=savegame)

    # Verify tax grouping structure
    tax_by_type = result["tax_by_building_type"]
    assert "House" in tax_by_type
    assert "Workshop" in tax_by_type

    # Check House group structure
    house_data = tax_by_type["House"]
    assert "buildings" in house_data
    assert "subtotal" in house_data
    assert len(house_data["buildings"]) == 2
    assert house_data["subtotal"] == 40  # 20 + 20

    # Find entries by name
    house_entries = house_data["buildings"]
    small_house_entry = next(e for e in house_entries if e["name"] == "Small House")
    large_house_entry = next(e for e in house_entries if e["name"] == "Large House")

    assert small_house_entry["level"] == 1
    assert small_house_entry["count"] == 2
    assert small_house_entry["taxes_per_building"] == 10
    assert small_house_entry["total"] == 20

    assert large_house_entry["level"] == 2
    assert large_house_entry["count"] == 1
    assert large_house_entry["taxes_per_building"] == 20
    assert large_house_entry["total"] == 20

    # Check Workshop group structure
    workshop_data = tax_by_type["Workshop"]
    assert "buildings" in workshop_data
    assert "subtotal" in workshop_data
    assert len(workshop_data["buildings"]) == 1
    assert workshop_data["subtotal"] == 15

    workshop_entry = workshop_data["buildings"][0]
    assert workshop_entry["name"] == "Blacksmith"
    assert workshop_entry["level"] == 1
    assert workshop_entry["count"] == 1
    assert workshop_entry["taxes_per_building"] == 15
    assert workshop_entry["total"] == 15


@pytest.mark.django_db
def test_get_balance_data_maintenance_grouping_by_building_type():
    """Test maintenance breakdown is grouped by building type and then by building."""
    savegame = SavegameFactory()

    # Create building types
    from apps.city.tests.factories import BuildingTypeFactory

    house_type = BuildingTypeFactory(name="House")
    wall_type = BuildingTypeFactory(name="Wall")

    # Create buildings with maintenance costs
    house1 = BuildingFactory(name="Small House", building_type=house_type, level=1, taxes=0, maintenance_costs=5)
    wall1 = BuildingFactory(name="Stone Wall", building_type=wall_type, level=1, taxes=0, maintenance_costs=3)

    # Place buildings on tiles
    TileFactory(savegame=savegame, building=house1)
    TileFactory(savegame=savegame, building=house1)
    TileFactory(savegame=savegame, building=house1)  # 3x Small House
    TileFactory(savegame=savegame, building=wall1)
    TileFactory(savegame=savegame, building=wall1)  # 2x Stone Wall

    result = get_balance_data(savegame=savegame)

    # Verify maintenance grouping structure
    maint_by_type = result["maintenance_by_building_type"]
    assert "House" in maint_by_type
    assert "Wall" in maint_by_type

    # Check House group structure
    house_data = maint_by_type["House"]
    assert "buildings" in house_data
    assert "subtotal" in house_data
    assert len(house_data["buildings"]) == 1
    assert house_data["subtotal"] == 15

    house_entry = house_data["buildings"][0]
    assert house_entry["name"] == "Small House"
    assert house_entry["level"] == 1
    assert house_entry["count"] == 3
    assert house_entry["maintenance_per_building"] == 5
    assert house_entry["total"] == 15

    # Check Wall group structure
    wall_data = maint_by_type["Wall"]
    assert "buildings" in wall_data
    assert "subtotal" in wall_data
    assert len(wall_data["buildings"]) == 1
    assert wall_data["subtotal"] == 6

    wall_entry = wall_data["buildings"][0]
    assert wall_entry["name"] == "Stone Wall"
    assert wall_entry["level"] == 1
    assert wall_entry["count"] == 2
    assert wall_entry["maintenance_per_building"] == 3
    assert wall_entry["total"] == 6


@pytest.mark.django_db
def test_get_balance_data_excludes_zero_tax_buildings_from_tax_grouping():
    """Test buildings with zero taxes are excluded from tax grouping."""
    savegame = SavegameFactory()

    from apps.city.tests.factories import BuildingTypeFactory

    house_type = BuildingTypeFactory(name="House")

    # Create building with zero taxes but non-zero maintenance
    building = BuildingFactory(name="House", building_type=house_type, level=1, taxes=0, maintenance_costs=10)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    # Should not appear in tax grouping
    assert result["tax_by_building_type"] == {}
    # Should appear in maintenance grouping
    assert "House" in result["maintenance_by_building_type"]


@pytest.mark.django_db
def test_get_balance_data_excludes_zero_maintenance_buildings_from_maintenance_grouping():
    """Test buildings with zero maintenance are excluded from maintenance grouping."""
    savegame = SavegameFactory()

    from apps.city.tests.factories import BuildingTypeFactory

    house_type = BuildingTypeFactory(name="House")

    # Create building with zero maintenance but non-zero taxes
    building = BuildingFactory(name="House", building_type=house_type, level=1, taxes=20, maintenance_costs=0)
    TileFactory(savegame=savegame, building=building)

    result = get_balance_data(savegame=savegame)

    # Should appear in tax grouping
    assert "House" in result["tax_by_building_type"]
    # Should not appear in maintenance grouping
    assert result["maintenance_by_building_type"] == {}


@pytest.mark.django_db
def test_get_balance_data_groups_empty_when_no_buildings():
    """Test grouping dictionaries are empty when no buildings exist."""
    savegame = SavegameFactory()
    TileFactory(savegame=savegame, building=None)

    result = get_balance_data(savegame=savegame)

    assert result["tax_by_building_type"] == {}
    assert result["maintenance_by_building_type"] == {}


@pytest.mark.django_db
def test_get_balance_data_grouping_sorted_alphabetically():
    """Test building types and buildings are sorted alphabetically."""
    savegame = SavegameFactory()

    from apps.city.tests.factories import BuildingTypeFactory

    # Create types in non-alphabetical order
    z_type = BuildingTypeFactory(name="Zzz Type")
    a_type = BuildingTypeFactory(name="Aaa Type")
    m_type = BuildingTypeFactory(name="Mmm Type")

    # Create buildings
    z_building = BuildingFactory(name="Zzz Building", building_type=z_type, level=1, taxes=10, maintenance_costs=0)
    a_building = BuildingFactory(name="Aaa Building", building_type=a_type, level=1, taxes=10, maintenance_costs=0)
    m_building = BuildingFactory(name="Mmm Building", building_type=m_type, level=1, taxes=10, maintenance_costs=0)

    TileFactory(savegame=savegame, building=z_building)
    TileFactory(savegame=savegame, building=a_building)
    TileFactory(savegame=savegame, building=m_building)

    result = get_balance_data(savegame=savegame)

    # Check that keys are sorted
    type_names = list(result["tax_by_building_type"].keys())
    assert type_names == ["Aaa Type", "Mmm Type", "Zzz Type"]


@pytest.mark.django_db
def test_get_balance_data_subtotals_calculated_correctly():
    """Test that subtotals are calculated correctly for each building type."""
    savegame = SavegameFactory()

    from apps.city.tests.factories import BuildingTypeFactory

    house_type = BuildingTypeFactory(name="House")

    # Create different house variants
    house1 = BuildingFactory(name="Small House", building_type=house_type, level=1, taxes=10, maintenance_costs=5)
    house2 = BuildingFactory(name="Large House", building_type=house_type, level=2, taxes=25, maintenance_costs=12)

    # Place multiple of each
    TileFactory(savegame=savegame, building=house1)
    TileFactory(savegame=savegame, building=house1)
    TileFactory(savegame=savegame, building=house1)  # 3x Small House
    TileFactory(savegame=savegame, building=house2)
    TileFactory(savegame=savegame, building=house2)  # 2x Large House

    result = get_balance_data(savegame=savegame)

    # Check tax subtotal: (3 * 10) + (2 * 25) = 30 + 50 = 80
    assert result["tax_by_building_type"]["House"]["subtotal"] == 80

    # Check maintenance subtotal: (3 * 5) + (2 * 12) = 15 + 24 = 39
    assert result["maintenance_by_building_type"]["House"]["subtotal"] == 39
