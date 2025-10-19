import random
from math import ceil

from django.contrib import messages

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.models import Savegame, Tile
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.WARNING
    TITLE = "Riots"

    initial_population: int
    lost_population: int
    demolished_buildings_count: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_population = self.savegame.population
        self.lost_population = ceil((random.randint(5, 10) / 100) * self.initial_population)
        self.demolished_buildings_count = random.randint(0, 2)
        self.affected_tiles = self._get_affected_tiles()

    def get_probability(self) -> int | float:
        return (
            super().get_probability() * self.savegame.unrest / 100
            if self.savegame.population > 0 and self.savegame.unrest >= 75
            else 0
        )

    def _get_affected_tiles(self) -> list[Tile]:
        """Get list of tiles with non-unique buildings that can be demolished."""
        tiles = list(
            self.savegame.tiles.filter(building__isnull=False, building__building_type__is_unique=False)[
                : self.demolished_buildings_count
            ]
        )
        return tiles

    def _prepare_effect_decrease_population(self) -> DecreasePopulationAbsolute:
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def _prepare_effect_remove_building_0(self) -> RemoveBuilding | None:
        """Remove first affected building if available."""
        if len(self.affected_tiles) > 0:
            return RemoveBuilding(tile=self.affected_tiles[0])
        return None

    def _prepare_effect_remove_building_1(self) -> RemoveBuilding | None:
        """Remove second affected building if available."""
        if len(self.affected_tiles) > 1:
            return RemoveBuilding(tile=self.affected_tiles[1])
        return None

    def _prepare_effect_remove_building_2(self) -> RemoveBuilding | None:
        """Remove third affected building if available."""
        if len(self.affected_tiles) > 2:
            return RemoveBuilding(tile=self.affected_tiles[2])
        return None

    def get_verbose_text(self) -> str:
        self.savegame.refresh_from_db()
        message = (
            f"The people have enough! Outraged mobs started fights in the streets which lead to the loss of "
            f"{self.initial_population - self.savegame.population} human lives."
        )
        if self.affected_tiles:
            demolished_count = len(self.affected_tiles)
            if demolished_count == 1:
                message += f" During the riots, {demolished_count} building was destroyed."
            else:
                message += f" During the riots, {demolished_count} buildings were destroyed."
        return message
