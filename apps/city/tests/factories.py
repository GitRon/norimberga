from pathlib import Path

import factory
from django.core.files import File

from apps.account.tests.factories import UserFactory
from apps.city.models import Building, BuildingType, Savegame, Terrain, Tile


class SavegameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Savegame

    user = factory.SubFactory(UserFactory)
    city_name = factory.Faker("city")
    coins = 1000
    population = 50
    unrest = 10
    current_year = 1150
    is_active = True

    @factory.post_generation
    def coat_of_arms(self, create, extracted, **kwargs):
        """Generate a coat of arms for the savegame if not provided."""
        if not create:
            return

        if extracted:
            # If a coat_of_arms was explicitly provided, use it
            self.coat_of_arms = extracted
            self.save()
            return

        # Create a simple dummy SVG for tests to avoid random mocking issues
        temp_path = Path(f"test_coat_of_arms_{self.id}.svg")
        temp_path.write_text('<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><rect fill="red"/></svg>')

        with temp_path.open("rb") as f:
            self.coat_of_arms.save(f"coat_of_arms_{self.id}.svg", File(f), save=True)

        temp_path.unlink()


class TerrainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Terrain

    name = factory.Faker("word")
    color_class = factory.Sequence(lambda n: f"bg-color-{n}")
    probability = factory.Faker("random_int", min=1, max=100)


class BuildingTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BuildingType
        skip_postgeneration_save = True

    name = factory.Faker("word")
    is_country = False
    is_city = True
    is_house = False
    is_wall = False
    is_unique = False

    @factory.post_generation
    def allowed_terrains(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for terrain in extracted:
                self.allowed_terrains.add(terrain)


class TileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tile

    savegame = factory.SubFactory(SavegameFactory)
    x = factory.Sequence(lambda n: (n * 17) % 1000)  # Use prime number for better distribution
    y = factory.Sequence(lambda n: (n * 23) % 1000)  # Use different prime for y
    terrain = factory.SubFactory(TerrainFactory)
    building = None


class BuildingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Building

    name = factory.Faker("word")
    building_type = factory.SubFactory(BuildingTypeFactory)
    level = 1
    taxes = 10
    building_costs = 50
    maintenance_costs = 5
    housing_space = 2


# Specialized factories
class RiverTerrainFactory(TerrainFactory):
    name = "River"
    is_water = True


class WaterTerrainFactory(TerrainFactory):
    name = "Water"
    is_water = True


class WallBuildingTypeFactory(BuildingTypeFactory):
    class Meta:
        model = BuildingType
        skip_postgeneration_save = True

    name = "Wall"
    is_wall = True
    is_city = True


class HouseBuildingTypeFactory(BuildingTypeFactory):
    class Meta:
        model = BuildingType
        skip_postgeneration_save = True

    name = "House"
    is_house = True
    is_city = True


class UniqueBuildingTypeFactory(BuildingTypeFactory):
    class Meta:
        model = BuildingType
        skip_postgeneration_save = True

    name = "Cathedral"
    is_unique = True
    is_city = True


class CountryBuildingTypeFactory(BuildingTypeFactory):
    class Meta:
        model = BuildingType
        skip_postgeneration_save = True

    name = "Farm"
    is_country = True
    is_city = False
