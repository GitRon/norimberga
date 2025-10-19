from django.db import models

from apps.savegame.models import Savegame


class Edict(models.Model):
    """Global template for edicts that can be activated by players."""

    name = models.CharField(max_length=100)
    description = models.TextField()

    # Costs (nullable means no cost for that resource)
    cost_coins = models.SmallIntegerField(null=True, blank=True)
    cost_population = models.SmallIntegerField(null=True, blank=True)

    # Effects (nullable means no effect on that resource)
    # Negative values reduce the resource, positive values increase it
    effect_unrest = models.SmallIntegerField(null=True, blank=True)
    effect_coins = models.SmallIntegerField(null=True, blank=True)
    effect_population = models.SmallIntegerField(null=True, blank=True)

    # Cooldown in years (nullable means no cooldown)
    cooldown_years = models.PositiveSmallIntegerField(null=True, blank=True)

    # Admin toggle
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


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
