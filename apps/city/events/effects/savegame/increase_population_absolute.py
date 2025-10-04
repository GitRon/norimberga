from apps.city.models import Savegame
from apps.city.services.building.housing import BuildingHousingService


class IncreasePopulationAbsolute:
    new_population: int

    def __init__(self, new_population: int):
        self.new_population = new_population

    def process(self, savegame: Savegame):
        max_population_housing = BuildingHousingService(savegame=savegame).calculate_max_space()
        savegame.population = min(savegame.population + self.new_population, max_population_housing)
        savegame.save()
