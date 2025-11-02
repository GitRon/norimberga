from django.db import models

from apps.edict.models.edict import Edict
from apps.savegame.models import Savegame


class EdictLog(models.Model):
    """Tracks when edicts are activated by specific savegames."""

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE, related_name="edict_logs")
    edict = models.ForeignKey(Edict, on_delete=models.CASCADE, related_name="logs")
    activated_at_year = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-activated_at_year"]
        indexes = [
            models.Index(fields=["savegame", "edict"]),
        ]

    def __str__(self) -> str:
        return f"{self.edict.name} activated in year {self.activated_at_year}"
