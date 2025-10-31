import random

from django.contrib import messages
from django.template.defaultfilters import pluralize

from apps.city.events.effects.building.remove_building import RemoveBuilding
from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.city.models import Tile
from apps.city.services.defense.calculation import DefenseCalculationService
from apps.city.services.prestige import PrestigeCalculationService
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 5  # Base probability, scaled by prestige-defense gap
    LEVEL = messages.ERROR
    TITLE = "Enemy Raid"

    prestige: int
    defense: int
    intensity: int
    initial_coins: int
    lost_coins: int
    lost_population: int
    increased_unrest: int
    affected_tiles: list[Tile]
    destroyed_building_count: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)

        # Calculate prestige and defense
        self.prestige = self._get_prestige()
        self.defense = self._get_defense()
        self.intensity = max(0, self.prestige - self.defense)

        self.initial_coins = self.savegame.coins

        # Losses scale with intensity (prestige-defense gap)
        # Base losses + intensity-based scaling
        intensity_multiplier = 1 + (self.intensity / 10)

        # Lose between 15-35% of current coins, scaled by intensity
        base_loss_percentage = random.randint(15, 35) / 100
        self.lost_coins = max(int(self.savegame.coins * base_loss_percentage * intensity_multiplier), 100)

        # Kill between 10-20% of population, scaled by intensity
        base_population_loss_percentage = random.randint(10, 20) / 100
        self.lost_population = max(
            int(self.savegame.population * base_population_loss_percentage * intensity_multiplier), 10
        )

        # Increase unrest by 10-20%, scaled by intensity
        base_unrest_increase = random.randint(10, 20)
        self.increased_unrest = min(int(base_unrest_increase * intensity_multiplier), 30)

        # Calculate how many buildings to destroy
        # Destroy 15-30% of city buildings, minimum 1, maximum 5
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
            destruction_percentage = random.randint(15, 30) / 100
            buildings_to_destroy = max(
                1, min(5, int(total_eligible_buildings * destruction_percentage * intensity_multiplier))
            )
        else:
            buildings_to_destroy = 0

        # Select random city buildings to destroy
        self.affected_tiles = list(eligible_tiles.order_by("?")[:buildings_to_destroy])
        self.destroyed_building_count = len(self.affected_tiles)

    def get_probability(self) -> int | float:
        """
        Event only occurs when prestige exceeds defense.
        Probability scales with the gap between prestige and defense (intensity).
        """
        if self.prestige <= self.defense:
            return 0

        # Scale probability by intensity: +1% per point of intensity
        # Example: 10 prestige vs 5 defense = 5 intensity = base 5% + 5% = 10% chance
        scaled_probability = super().get_probability() + self.intensity
        return min(scaled_probability, 50)  # Cap at 50% to avoid certainty

    def _prepare_effect_decrease_coins(self) -> DecreaseCoins:
        return DecreaseCoins(coins=self.lost_coins)

    def _prepare_effect_decrease_population(self) -> DecreasePopulationAbsolute:
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def _prepare_effect_increase_unrest(self) -> IncreaseUnrestAbsolute:
        return IncreaseUnrestAbsolute(additional_unrest=self.increased_unrest)

    def get_effects(self) -> list:
        """Override to dynamically add building removal effects."""
        effects = [
            self._prepare_effect_decrease_coins(),
            self._prepare_effect_decrease_population(),
            self._prepare_effect_increase_unrest(),
        ]

        # Add a RemoveBuilding effect for each affected tile
        effects.extend([RemoveBuilding(tile=tile) for tile in self.affected_tiles])

        return effects

    def get_verbose_text(self) -> str:
        self.savegame.refresh_from_db()
        message = (
            f"Your city's wealth and prestige ({self.prestige}) attracted enemy forces! "
            f"With only {self.defense} defense, the raiders overwhelmed your guards. "
            f"They stole {self.initial_coins - self.savegame.coins} coins and killed "
            f"{self.lost_population} inhabitants. "
            f"Unrest increased by {self.increased_unrest}%."
        )
        if self.destroyed_building_count > 0:
            message += (
                f" {self.destroyed_building_count} building{pluralize(self.destroyed_building_count)} "
                f"{'was' if self.destroyed_building_count == 1 else 'were'} destroyed during the raid."
            )

        return message

    def _get_prestige(self) -> int:
        """Get current prestige value."""
        service = PrestigeCalculationService(savegame=self.savegame)
        return service.process()

    def _get_defense(self) -> int:
        """Get current defense value."""
        service = DefenseCalculationService(savegame=self.savegame)
        return service.process()
