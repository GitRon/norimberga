from pathlib import Path

import factory
from django.core.files import File

from apps.account.tests.factories import UserFactory
from apps.savegame.models import PendingSiege, Savegame, SiegeChronicle


class SavegameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Savegame
        skip_postgeneration_save = True

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


class PendingSiegeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PendingSiege

    savegame = factory.SubFactory(SavegameFactory)
    attack_year = 1153
    actual_strength = 150
    announced_strength = 150
    direction = PendingSiege.Direction.NORTH
    resolved = False


class SiegeChronicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SiegeChronicle

    savegame = factory.SubFactory(SavegameFactory)
    year = 1153
    direction = "N"
    attacker_strength = 150
    defense_score = 200
    result = SiegeChronicle.Result.REPELLED
    report_text = "The enemy was repelled at the North wall."
