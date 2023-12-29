from apps.city.models import Savegame


class DecreasePopulationAbsolute:
    lost_population: int

    def __init__(self, lost_population: int):
        self.lost_population = lost_population

    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)
        savegame.population = max(savegame.population - self.lost_population, 0)
        savegame.save()
