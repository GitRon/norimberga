import factory

from apps.city.tests.factories import SavegameFactory
from apps.edict.models import Edict, EdictLog


class EdictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Edict

    name = factory.Sequence(lambda n: f"Edict {n}")
    description = factory.Faker("sentence")
    cost_coins = None
    cost_population = None
    effect_unrest = None
    effect_coins = None
    effect_population = None
    cooldown_years = None
    is_active = True


class EdictLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EdictLog

    savegame = factory.SubFactory(SavegameFactory)
    edict = factory.SubFactory(EdictFactory)
    activated_at_year = factory.Faker("random_int", min=1000, max=1500)
