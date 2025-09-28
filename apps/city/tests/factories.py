import factory
from django.contrib.auth.models import User

from apps.city.models import Building, BuildingType, Savegame, Terrain, Tile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class SavegameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Savegame

    city_name = factory.Faker("city")
    map_size = 5
    coins = 100
    population = 50
    unrest = 10
    current_year = 1150
    is_active = True


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
