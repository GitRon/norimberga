from apps.city.models import Savegame


class IncreaseUnrestAbsolute:
    additional_unrest: int

    def __init__(self, additional_unrest: int):
        self.additional_unrest = additional_unrest

    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)
        savegame.unrest = min(savegame.unrest + self.additional_unrest, 100)
        savegame.save()
