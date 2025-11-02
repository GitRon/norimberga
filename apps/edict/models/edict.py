from django.db import models


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

    # Optional milestone requirement (nullable means no milestone required)
    required_milestone = models.ForeignKey(
        "milestone.Milestone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edicts",
        help_text="Milestone that must be completed before this edict becomes available",
    )

    # Optional prestige requirement (nullable means no prestige required)
    required_prestige = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Minimum prestige required before this edict becomes available",
    )

    # Admin toggle
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
