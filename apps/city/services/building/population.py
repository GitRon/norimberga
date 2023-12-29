from math import ceil

from apps.city.models import Building, Savegame


class BuildingPopulationService:
    # TODO(RV): service calculates max housing AND increases pop during round -> split up
    MAX_POP_PER_HOUSE = 150
    YEARLY_POP_INCREASE_FACTOR = 0.05

    def __init__(self):
        super().__init__()

        self.savegame, _ = Savegame.objects.get_or_create(id=1)

    def _calculate_no_houses(self):
        return self.savegame.tiles.filter(building__behaviour_type=Building.BehaviourTypeChoices.IS_HOUSE).count()

    def calculate_max_space(self):
        # TODO(RV): sterben alle direkt, wenn kein platz mehr ist? informieren wir den user?
        no_houses = self._calculate_no_houses()
        return no_houses * self.MAX_POP_PER_HOUSE

    def process(self):
        max_space = self.calculate_max_space()

        new_pop = min(ceil(self.savegame.population * (1 + self.YEARLY_POP_INCREASE_FACTOR)), max_space)

        self.savegame.population = new_pop
        self.savegame.save()
