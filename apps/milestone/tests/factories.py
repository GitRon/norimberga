import factory

from apps.milestone.models import Milestone, MilestoneCondition, MilestoneLog
from apps.savegame.tests.factories import SavegameFactory


class MilestoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Milestone

    name = factory.Sequence(lambda n: f"Milestone {n}")
    description = factory.Faker("sentence")
    parent = None
    order = factory.Sequence(lambda n: n)


class MilestoneConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MilestoneCondition

    milestone = factory.SubFactory(MilestoneFactory)
    condition_class = "apps.milestone.conditions.population.MinPopulationCondition"
    value = "50"


class MilestoneLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MilestoneLog

    savegame = factory.SubFactory(SavegameFactory)
    milestone = factory.SubFactory(MilestoneFactory)
    accomplished_at = factory.Faker("random_int", min=1000, max=1500)
