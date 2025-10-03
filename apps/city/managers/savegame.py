from django.db import models
from django.db.models import Sum


class SavegameQuerySet(models.QuerySet):
    pass


class SavegameManager(models.Manager):
    def aggregate_taxes(self, savegame):
        """Aggregate total tax income from all buildings in the savegame."""
        result = savegame.tiles.aggregate(sum_taxes=Sum("building__taxes"))["sum_taxes"]
        # Avoid leaking None from ORM
        return result if result is not None else 0

    def aggregate_maintenance_costs(self, savegame):
        """Aggregate total maintenance costs from all buildings in the savegame."""
        result = savegame.tiles.aggregate(sum_maintenance=Sum("building__maintenance_costs"))["sum_maintenance"]
        # Avoid leaking None from ORM
        return result if result is not None else 0


SavegameManager = SavegameManager.from_queryset(SavegameQuerySet)
