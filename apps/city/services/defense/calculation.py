from dataclasses import dataclass

from apps.city.models import Tile
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.city.services.wall.shape_bonus import WallShapeBonusService
from apps.city.services.wall.spike_malus import WallSpikeMalusService
from apps.savegame.models import Savegame


@dataclass(kw_only=True)
class DefenseBreakdown:
    """Detailed breakdown of defense calculation."""

    is_enclosed: bool
    base_defense: int
    shape_bonus: int
    spike_malus: int
    potential_total: int  # Total if enclosed (ignoring enclosure requirement)
    actual_total: int  # Actual defense value (0 if not enclosed)


class DefenseCalculationService:
    """
    Service to calculate total defense value for a savegame.

    Defense calculation rules:
    1. If city walls are not enclosed, defense value is 0
    2. If walls are enclosed, sum defense_value from all buildings
    3. Add shape bonus for well-formed walls (smooth connections)
    4. Subtract spike malus for poorly connected walls (0-1 neighbors)

    Uses dependency injection for testability.
    """

    def __init__(
        self,
        *,
        savegame: Savegame,
        enclosure_service: WallEnclosureService | None = None,
        shape_bonus_service: WallShapeBonusService | None = None,
        spike_malus_service: WallSpikeMalusService | None = None,
    ):
        self.savegame = savegame
        self.enclosure_service = enclosure_service or WallEnclosureService(savegame=savegame)
        self.shape_bonus_service = shape_bonus_service or WallShapeBonusService(savegame=savegame)
        self.spike_malus_service = spike_malus_service or WallSpikeMalusService(savegame=savegame)

    def process(self) -> int:
        """
        Calculate total defense value.

        Returns:
            Total defense points (0 if walls not enclosed)
        """
        breakdown = self.get_breakdown()
        return breakdown.actual_total

    def get_breakdown(self) -> DefenseBreakdown:
        """
        Get detailed breakdown of defense calculation.

        Returns:
            DefenseBreakdown with all components
        """
        # Check if walls are enclosed
        is_enclosed = self.enclosure_service.process()

        # Calculate all components regardless of enclosure
        base_defense = self._calculate_base_defense()
        shape_bonus = self.shape_bonus_service.process()
        spike_malus = self.spike_malus_service.process()

        # Calculate potential total (what defense would be if enclosed)
        potential_total = max(0, base_defense + shape_bonus + spike_malus)

        # Actual total is 0 if not enclosed, otherwise use potential total
        actual_total = potential_total if is_enclosed else 0

        return DefenseBreakdown(
            is_enclosed=is_enclosed,
            base_defense=base_defense,
            shape_bonus=shape_bonus,
            spike_malus=spike_malus,
            potential_total=potential_total,
            actual_total=actual_total,
        )

    def _calculate_base_defense(self) -> int:
        """
        Calculate base defense from all buildings with defense_value.
        """
        tiles_with_buildings = Tile.objects.filter(savegame=self.savegame, building__isnull=False).select_related(
            "building"
        )

        total_defense = sum(tile.building.defense_value for tile in tiles_with_buildings)

        return total_defense
