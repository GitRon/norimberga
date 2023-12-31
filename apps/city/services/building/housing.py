from django.db.models import Sum

from apps.city.models import Savegame


class BuildingHousingService:
    def __init__(self):
        super().__init__()

        self.savegame, _ = Savegame.objects.get_or_create(id=1)

    def calculate_max_space(self):
        # TODO(RV): create event that tells the user that the homeless people have moved out of the city or increase
        #  unrest -> change event effect that homelessness is possible (dont check max)
        return self.savegame.tiles.aggregate(sum_space=Sum("building__housing_space"))["sum_space"]
