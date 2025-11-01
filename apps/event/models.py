from django.db import models

from apps.savegame.models import Savegame


class EventNotification(models.Model):
    """
    Persistent notification generated from game events.
    Users must acknowledge each notification before continuing gameplay.
    """

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField("Year when event occurred")
    title = models.CharField("Event title", max_length=100)
    message = models.TextField("Event message")
    acknowledged = models.BooleanField("Acknowledged", default=False)

    class Meta:
        default_related_name = "event_notifications"
        ordering = ["year"]
        indexes = [
            models.Index(fields=["savegame", "acknowledged"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} (Year {self.year})"
