from django.db import models

from apps.savegame.managers.pending_siege import PendingSiegeManager
from apps.savegame.models.savegame import Savegame


class PendingSiege(models.Model):
    class Direction(models.TextChoices):
        NORTH = "N", "North"
        SOUTH = "S", "South"
        EAST = "E", "East"
        WEST = "W", "West"

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    attack_year = models.PositiveSmallIntegerField()
    actual_strength = models.PositiveSmallIntegerField()
    announced_strength = models.PositiveSmallIntegerField()
    direction = models.CharField(max_length=1, choices=Direction.choices)
    resolved = models.BooleanField(default=False)

    objects = PendingSiegeManager()

    class Meta:
        default_related_name = "pending_sieges"

    def __str__(self) -> str:
        return f"Siege on {self.savegame} (year {self.attack_year}, {self.direction})"
