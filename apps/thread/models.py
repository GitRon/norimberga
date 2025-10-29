from django.db import models

from apps.savegame.models import Savegame


class ThreadType(models.Model):
    """
    Global thread type definition that applies to all savegames.
    Each thread type represents a potential threat or challenge condition.
    """

    name = models.CharField("Name", max_length=100, unique=True)
    description = models.TextField("Description", blank=True)
    condition_class = models.CharField(
        "Condition class",
        max_length=200,
        help_text="Python class path (e.g., 'apps.thread.conditions.prestige_defense.PrestigeDefenseThread')",
    )
    severity = models.CharField(
        "Severity",
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="medium",
    )
    order = models.PositiveSmallIntegerField("Order", default=0, help_text="Display order")

    class Meta:
        default_related_name = "thread_types"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name


class ActiveThread(models.Model):
    """
    Savegame-specific tracking of currently active threads.
    A thread becomes active when its condition is met.
    """

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    thread_type = models.ForeignKey(ThreadType, on_delete=models.CASCADE)
    activated_at = models.PositiveSmallIntegerField("Activated at", help_text="Year when thread became active")
    intensity = models.PositiveIntegerField(
        "Intensity", default=0, help_text="How severe the thread is (e.g., Prestige - Defense)"
    )

    class Meta:
        default_related_name = "active_threads"
        unique_together = ("savegame", "thread_type")
        ordering = ["-intensity", "thread_type__order"]

    def __str__(self) -> str:
        return f"{self.savegame.city_name}: {self.thread_type.name} (Intensity: {self.intensity})"
