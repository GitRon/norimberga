from apps.city.models import Savegame


class DecreaseUnrestAbsolute:
    lost_unrest: int

    def __init__(self, lost_unrest: int):
        self.lost_unrest = lost_unrest

    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)
        savegame.unrest = max(savegame.unrest - self.lost_unrest, 0)
        savegame.save()
