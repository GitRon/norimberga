from math import ceil

from apps.city.models import Building, Savegame


class BuildingPopulationService:
    MAX_POP_PER_HOUSE = 150
    YEARLY_POP_INCREASE_FACTOR = 0.05

    def __init__(self):
        super().__init__()

        self.savegame, _ = Savegame.objects.get_or_create(id=1)

    def _calculate_no_houses(self):
        return self.savegame.tiles.filter(building__behaviour_type=Building.BehaviourTypeChoices.IS_HOUSE).count()

    def _calculate_max_space(self, no_houses: int):
        return no_houses * self.MAX_POP_PER_HOUSE

    def process(self):
        no_houses = self._calculate_no_houses()

        max_space = self._calculate_max_space(no_houses=no_houses)

        new_pop = min(ceil(self.savegame.population * (1 + self.YEARLY_POP_INCREASE_FACTOR)), max_space)

        self.savegame.population = new_pop
        self.savegame.save()
