from apps.city.models import Savegame


class DecreasePopulationRelative:
    lost_population: float

    def __init__(self, lost_population_percentage: float):
        self.lost_population = lost_population_percentage

    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)
        savegame.population = max(round(savegame.population * (1 - self.lost_population)), 0)
        savegame.save()
