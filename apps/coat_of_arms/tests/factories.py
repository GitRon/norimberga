import factory

from apps.coat_of_arms.services.generator import HeraldicShield


class HeraldicShieldFactory(factory.Factory):
    class Meta:
        model = HeraldicShield

    shape = factory.Faker("random_element", elements=["heater", "round", "kite"])
    division = factory.Faker("random_element", elements=["plain", "per pale", "per fess", "quarterly"])
    tinctures = factory.LazyFunction(lambda: ["gules", "argent"])
    charges = factory.LazyFunction(lambda: ["lion rampant"])
    motto = factory.Faker("random_element", elements=["Fortune favors the bold", "Honor and Glory", None])
