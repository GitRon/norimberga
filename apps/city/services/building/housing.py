from apps.city.models import Building, Savegame


class BuildingHousingService:
    MAX_POP_PER_HOUSE = 150

    def __init__(self):
        super().__init__()

        self.savegame, _ = Savegame.objects.get_or_create(id=1)

    def _calculate_no_houses(self):
        return self.savegame.tiles.filter(building__behaviour_type=Building.BehaviourTypeChoices.IS_HOUSE).count()

    def calculate_max_space(self):
        # TODO(RV): create event that tells the user that the homeless people have moved out of the city or increase
        #  unrest
        no_houses = self._calculate_no_houses()
        return no_houses * self.MAX_POP_PER_HOUSE
