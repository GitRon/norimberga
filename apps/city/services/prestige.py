from apps.savegame.models import Savegame


class PrestigeCalculationService:
    """
    Calculates the total prestige for a savegame based on buildings.
    """

    def __init__(self, *, savegame: Savegame) -> None:
        self.savegame = savegame

    def process(self) -> int:
        """
        Calculate and return the total prestige from all buildings in the savegame.
        """
        tiles_with_buildings = self.savegame.tiles.filter(building__isnull=False).select_related("building")

        total_prestige = sum(tile.building.prestige for tile in tiles_with_buildings)

        return total_prestige
