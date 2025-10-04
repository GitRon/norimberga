from django.db.models import Sum

from apps.city.models import Savegame


class BuildingHousingService:
    def __init__(self, *, savegame: Savegame):
        super().__init__()
        self.savegame = savegame

    def calculate_max_space(self) -> int | None:
        # TODO(RV): create event that tells the user that the homeless people have moved out of the city or increase
        #  unrest -> change event effect that homelessness is possible (dont check max)
        return self.savegame.tiles.aggregate(sum_space=Sum("building__housing_space"))["sum_space"]
