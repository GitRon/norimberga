import pytest

from apps.city.models import Building, BuildingType


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure the database for tests."""


@pytest.fixture
def ruins_building(db):
    """Create the Ruins building in the test database.

    This fixture ensures the Ruins building (pk=28) exists, which is required
    by the RemoveBuilding effect to replace damaged buildings with ruins.
    """
    # Create Ruins BuildingType
    ruins_type = BuildingType.objects.create(
        pk=10,
        name="Ruins",
        is_country=False,
        is_city=False,
        is_house=False,
        is_wall=False,
        is_unique=True,
    )

    # Create Ruins Building
    ruins = Building.objects.create(
        pk=28,
        name="Ruins",
        building_type=ruins_type,
        level=1,
        taxes=0,
        building_costs=0,
        demolition_costs=20,
        maintenance_costs=0,
        housing_space=0,
    )

    return ruins
