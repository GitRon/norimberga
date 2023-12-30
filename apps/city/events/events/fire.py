import random

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.models import Building, Savegame, Tile
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 5

    savegame: Savegame
    initial_population: int
    lost_population: int
    affected_tile: Tile

    def __init__(self):
        super().__init__()
        self.savegame, _ = Savegame.objects.get_or_create(id=1)
        self.initial_population = self.savegame.population

        self.lost_population = random.randint(10, 50)
        self.affected_tile = self.savegame.tiles.filter(
            building__behaviour_type=Building.BehaviourTypeChoices.IS_HOUSE
        ).first()

    def get_probability(self):
        return super().get_probability() if self.savegame.population > 0 else 0

    def _prepare_effect_decrease_population(self):
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def _prepare_effect_remove_building(self):
        if self.affected_tile:
            return RemoveBuilding(tile=self.affected_tile)
        return None

    def get_verbose_text(self):
        self.savegame.refresh_from_db()
        message = (
            f"Due to general neglect, a fire raged throughout the city, killing "
            f"{self.initial_population - self.savegame.population} citizens."
        )
        if self.affected_tile:
            message += f" The fire started in the building {self.affected_tile} and destroyed it completely."

        return message
