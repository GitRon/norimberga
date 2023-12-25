from django.db.models import Sum

from apps.city.models import Savegame


class BuildingMaintenanceService:
    def __init__(self):
        super().__init__()

        self.savegame, _ = Savegame.objects.get_or_create(id=1)

    def _calculate_taxes(self):
        return self.savegame.tiles.aggregate(sum_taxes=Sum("building__taxes"))["sum_taxes"]

    def _calculate_maintenance(self):
        return self.savegame.tiles.aggregate(sum_maintenance=Sum("building__maintenance_costs"))["sum_maintenance"]

    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)

        savegame.coins += self._calculate_taxes() - self._calculate_maintenance()
        savegame.current_year += 1

        savegame.save()
