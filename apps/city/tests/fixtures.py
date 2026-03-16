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
        Terrain.objects.create(name=f"Terrain {i}", image_filename=f"terrain-{i}.png", probability=10)
        for i in range(1, 8)
    ]

    # Get or create Ruins BuildingType (may already exist in reused test DB from fixtures)
    ruins_type, created = BuildingType.objects.get_or_create(
        type=BuildingType.Type.RUINS,
        defaults={
            "name": "Ruins",
            "is_country": False,
            "is_city": False,
            "is_house": False,
            "is_wall": False,
            "is_unique": False,
        },
    )
    if created:
        ruins_type.allowed_terrains.set(terrains)

    # Get or create Ruins Building
    ruins = ruins_type.buildings.first()
    if ruins is None:
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
