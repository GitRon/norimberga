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
    color_class = factory.Faker("color_name")
    probability = factory.Faker("random_int", min=1, max=100)


class BuildingTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BuildingType

    name = factory.Faker("word")
    is_country = False
    is_city = True


class TileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tile

    savegame = factory.SubFactory(SavegameFactory)
    coordinate_x = factory.Faker("random_int", min=0, max=4)
    coordinate_y = factory.Faker("random_int", min=0, max=4)
    tile_type = factory.SubFactory(TerrainFactory)


class BuildingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Building

    building_type = factory.SubFactory(BuildingTypeFactory)
    tile = factory.SubFactory(TileFactory)
    building_costs = 50
    maintenance_costs = 5
    taxes = 10
    housing_space = 2
    level = 1