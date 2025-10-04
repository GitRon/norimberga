from apps.city.models import Savegame
from apps.city.services.building.housing import BuildingHousingService


class IncreasePopulationRelative:
    new_population: float

    def __init__(self, new_population_percentage: float):
        self.new_population = new_population_percentage

    def process(self, savegame: Savegame):
        max_population_housing = BuildingHousingService(savegame=savegame).calculate_max_space()
        savegame.population = min(round(savegame.population * (1 + self.new_population)), max_population_housing)
        savegame.save()
