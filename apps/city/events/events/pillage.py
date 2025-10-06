import random

from django.contrib import messages
from django.template.defaultfilters import pluralize

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.models import Savegame, Tile
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 30
    LEVEL = messages.ERROR
    TITLE = "Pillage"

    initial_coins: int
    lost_coins: int
    lost_population: int
    affected_tiles: list[Tile]
    destroyed_building_count: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_coins = self.savegame.coins

        # Lose between 10-30% of current coins, minimum 50
        loss_percentage = random.randint(10, 30) / 100
        self.lost_coins = max(int(self.savegame.coins * loss_percentage), 50)

        # Kill between 5-15% of population, minimum 5
        population_loss_percentage = random.randint(5, 15) / 100
        self.lost_population = max(int(self.savegame.population * population_loss_percentage), 5)

        # Calculate how many buildings to destroy based on total buildings
        # Destroy 10-25% of city buildings, minimum 1, maximum 5
        # Only target pure city buildings (exclude walls, country buildings, unique buildings)
        eligible_tiles = (
            self.savegame.tiles.filter(building__isnull=False)
            .filter(building__building_type__is_city=True)
            .exclude(building__building_type__is_wall=True)
            .exclude(building__building_type__is_country=True)
            .exclude(building__building_type__is_unique=True)
        )
        total_eligible_buildings = eligible_tiles.count()

        if total_eligible_buildings > 0:
            destruction_percentage = random.randint(10, 25) / 100
            buildings_to_destroy = max(1, min(5, int(total_eligible_buildings * destruction_percentage)))
        else:
            buildings_to_destroy = 0

        # Select random city buildings to destroy
        self.affected_tiles = list(eligible_tiles.order_by("?")[:buildings_to_destroy])

        self.destroyed_building_count = len(self.affected_tiles)

    def get_probability(self) -> int | float:
        # Only occurs when city is not enclosed by walls
        return super().get_probability() if not self.savegame.is_enclosed else 0

    def _prepare_effect_decrease_coins(self) -> DecreaseCoins:
        return DecreaseCoins(coins=self.lost_coins)

    def _prepare_effect_decrease_population(self) -> DecreasePopulationAbsolute:
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def get_effects(self) -> list:
        """Override to dynamically add building removal effects."""
        effects = [
            self._prepare_effect_decrease_coins(),
            self._prepare_effect_decrease_population(),
        ]

        # Add a RemoveBuilding effect for each affected tile
        effects.extend([RemoveBuilding(tile=tile) for tile in self.affected_tiles])

        return effects

    def get_verbose_text(self) -> str:
        self.savegame.refresh_from_db()
        message = (
            f"Without a protective wall, raiders pillaged the city! "
            f"They stole {self.initial_coins - self.savegame.coins} coins and killed "
            f"{self.lost_population} inhabitants."
        )
        if self.destroyed_building_count > 0:
            message += (
                f" {self.destroyed_building_count} building{pluralize(self.destroyed_building_count)} "
                f"{'was' if self.destroyed_building_count == 1 else 'were'} destroyed during the raid."
            )

        return message
