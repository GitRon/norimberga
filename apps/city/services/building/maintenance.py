from django.db.models import Sum

from apps.city.models import Savegame


class BuildingMaintenanceService:
    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)

        sum_maintenance = savegame.tiles.aggregate(sum_maintenance=Sum("building__maintenance_costs"))[
            "sum_maintenance"
        ]

        print(f"Maintenance {sum_maintenance}")

        savegame.coins -= sum_maintenance
        savegame.save()

        return sum_maintenance
