import typing

from django.db import models
from django.db.models import Sum

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

    from apps.savegame.models import Savegame


class SavegameQuerySet(models.QuerySet):
    def filter_active_for_user(self, *, user: "AbstractBaseUser") -> models.QuerySet:
        return self.filter(user=user, is_active=True)


class SavegameManager(models.Manager):
    def get_active_for_user(self, *, user: "AbstractBaseUser") -> "Savegame | None":
        return self.filter_active_for_user(user=user).first()

    def aggregate_taxes(self, *, savegame) -> int:
        """Aggregate total tax income from all buildings in the savegame."""
        result = savegame.tiles.aggregate(sum_taxes=Sum("building__taxes"))["sum_taxes"]
        # Avoid leaking None from ORM
        return result if result is not None else 0

    def aggregate_maintenance_costs(self, *, savegame) -> int:
        """Aggregate total maintenance costs from all buildings in the savegame."""
        result = savegame.tiles.aggregate(sum_maintenance=Sum("building__maintenance_costs"))["sum_maintenance"]
        # Avoid leaking None from ORM
        return result if result is not None else 0


SavegameManager = SavegameManager.from_queryset(SavegameQuerySet)
