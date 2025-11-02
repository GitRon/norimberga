import pytest
from django.core.exceptions import ValidationError

from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory


# Building Model Tests
@pytest.mark.django_db
def test_building_str_representation():
    """Test __str__ method returns building name."""
    building = BuildingFactory(name="Test House")
    assert str(building) == "Test House"


@pytest.mark.django_db
def test_building_creation_with_all_fields():
    """Test building creation with all fields."""
    building_type = BuildingTypeFactory.create()
    building = BuildingFactory(
        name="Manor",
        building_type=building_type,
        level=2,
        taxes=20,
        building_costs=100,
        maintenance_costs=10,
        housing_space=4,
    )

    assert building.name == "Manor"
    assert building.building_type == building_type
    assert building.level == 2
    assert building.taxes == 20
    assert building.building_costs == 100
    assert building.maintenance_costs == 10
    assert building.housing_space == 4


@pytest.mark.django_db
def test_building_validator_minimum_values():
    """Test building validators prevent negative values."""
    # Test taxes validator
    building = BuildingFactory.build(taxes=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)

    # Test building_costs validator
    building = BuildingFactory.build(building_costs=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)

    # Test maintenance_costs validator
    building = BuildingFactory.build(maintenance_costs=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)

    # Test housing_space validator
    building = BuildingFactory.build(housing_space=-1)
    with pytest.raises(ValidationError) as exc_info:
        building.full_clean()
    assert "Ensure this value is greater than or equal to 0" in str(exc_info.value)
