import factory

from apps.city.tests.factories import SavegameFactory
from apps.milestone.models import MilestoneLog


class MilestoneLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MilestoneLog

    savegame = factory.SubFactory(SavegameFactory)
    milestone = factory.Faker("sentence", nb_words=3)
    accomplished_at = factory.Faker("random_int", min=1000, max=1500)
