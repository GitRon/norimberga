from apps.city.models import Tile
from apps.city.services.wall.enclosure import WallEnclosureService
from apps.city.services.wall.shape_bonus import WallShapeBonusService
from apps.savegame.models import Savegame


class DefenseCalculationService:
    """
    Service to calculate total defense value for a savegame.

    Defense calculation rules:
    1. If city walls are not enclosed, defense value is 0
    2. If walls are enclosed, sum defense_value from all buildings
    3. Add shape bonus for well-formed walls (smooth connections)

    Uses dependency injection for testability.
    """

    def __init__(
        self,
        *,
        savegame: Savegame,
        enclosure_service: WallEnclosureService | None = None,
        shape_bonus_service: WallShapeBonusService | None = None,
    ):
        self.savegame = savegame
        self.enclosure_service = enclosure_service or WallEnclosureService(savegame=savegame)
        self.shape_bonus_service = shape_bonus_service or WallShapeBonusService(savegame=savegame)

    def process(self) -> int:
        """
        Calculate total defense value.

        Returns:
            Total defense points (0 if walls not enclosed)
        """
        # Check if walls are enclosed
        is_enclosed = self.enclosure_service.process()

        if not is_enclosed:
            return 0

        # Sum defense values from all buildings
        base_defense = self._calculate_base_defense()

        # Add shape bonus
        shape_bonus = self.shape_bonus_service.process()

        return base_defense + shape_bonus

    def _calculate_base_defense(self) -> int:
        """
        Calculate base defense from all buildings with defense_value.
        """
        tiles_with_buildings = Tile.objects.filter(savegame=self.savegame, building__isnull=False).select_related(
            "building"
        )

        total_defense = sum(tile.building.defense_value for tile in tiles_with_buildings)

        return total_defense
