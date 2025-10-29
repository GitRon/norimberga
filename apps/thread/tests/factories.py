import factory

from apps.savegame.tests.factories import SavegameFactory
from apps.thread.models import ActiveThread, ThreadType


class ThreadTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ThreadType

    name = factory.Sequence(lambda n: f"Thread Type {n}")
    description = factory.Faker("sentence")
    condition_class = "apps.thread.conditions.prestige_defense.PrestigeDefenseThread"
    severity = "medium"
    order = factory.Sequence(lambda n: n)


class ActiveThreadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActiveThread

    savegame = factory.SubFactory(SavegameFactory)
    thread_type = factory.SubFactory(ThreadTypeFactory)
    activated_at = factory.Faker("random_int", min=1000, max=1500)
    intensity = factory.Faker("random_int", min=1, max=100)
