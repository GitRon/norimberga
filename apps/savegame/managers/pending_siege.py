import typing

from django.db import models

if typing.TYPE_CHECKING:
    from apps.savegame.models import PendingSiege, Savegame


class PendingSiegeQuerySet(models.QuerySet):
    def filter_unresolved(self) -> models.QuerySet:
        return self.filter(resolved=False)

    def filter_by_year(self, *, year: int) -> models.QuerySet:
        return self.filter(attack_year=year)


class PendingSiegeManager(models.Manager):
    def get_due_siege(self, *, savegame: "Savegame", year: int) -> "PendingSiege | None":
        return self.filter(savegame=savegame).filter_unresolved().filter_by_year(year=year).first()

    def create_pending_siege(
        self,
        *,
        savegame: "Savegame",
        attack_year: int,
        actual_strength: int,
        announced_strength: int,
        direction: str,
    ) -> "PendingSiege":
        return self.create(
            savegame=savegame,
            attack_year=attack_year,
            actual_strength=actual_strength,
            announced_strength=announced_strength,
            direction=direction,
        )


PendingSiegeManager = PendingSiegeManager.from_queryset(PendingSiegeQuerySet)
