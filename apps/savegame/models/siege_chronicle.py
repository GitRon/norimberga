from django.db import models

from apps.savegame.managers.siege_chronicle import SiegeChronicleManager
from apps.savegame.models.savegame import Savegame


class SiegeChronicle(models.Model):
    class Result(models.TextChoices):
        REPELLED = "repelled", "Repelled"
        DAMAGED = "damaged", "Wall Damaged"
        BREACHED = "breached", "Wall Breached"

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    direction = models.CharField(max_length=1, choices=[("N", "North"), ("S", "South"), ("E", "East"), ("W", "West")])
    attacker_strength = models.PositiveSmallIntegerField()
    defense_score = models.PositiveSmallIntegerField()
    result = models.CharField(max_length=10, choices=Result.choices)
    report_text = models.TextField()

    objects = SiegeChronicleManager()

    class Meta:
        default_related_name = "siege_chronicles"
        ordering = ["year"]

    def __str__(self) -> str:
        return f"Siege Chronicle {self.year} ({self.savegame})"
