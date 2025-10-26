import pytest

from apps.city.models import Building, BuildingType, Terrain


@pytest.fixture
def ruins_building(db):
    """Create the Ruins building for tests.

    In production, this exists from fixtures (building_types.json and buildings.json).
    For tests, we create it on demand since fixtures aren't loaded by default.
    """
    # Create all terrains first (ruins can be placed on any terrain)
    terrains = [
        Terrain.objects.create(name=f"Terrain {i}", color_class=f"bg-test-{i}", probability=10) for i in range(1, 8)
    ]

    # Create Ruins BuildingType
    ruins_type = BuildingType.objects.create(
        name="Ruins",
        type=BuildingType.Type.RUINS,
        is_country=False,
        is_city=False,
        is_house=False,
        is_wall=False,
        is_unique=False,
    )
    ruins_type.allowed_terrains.set(terrains)

    # Create Ruins Building
    ruins = Building.objects.create(
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
