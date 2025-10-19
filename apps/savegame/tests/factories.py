import factory

from apps.account.tests.factories import UserFactory
from apps.savegame.models import Savegame


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
