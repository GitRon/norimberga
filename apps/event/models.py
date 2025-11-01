from django.db import models

from apps.savegame.models import Savegame


class EventNotification(models.Model):
    """
    Persistent notification generated from game events.
    Users must acknowledge each notification before continuing gameplay.
    """

    class Level(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        WARNING = "warning", "Warning"
        INFO = "info", "Info"

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField("Year when event occurred")
    title = models.CharField("Event title", max_length=100)
    message = models.TextField("Event message")
    level = models.CharField("Message level", max_length=10, choices=Level.choices, default=Level.INFO)
    acknowledged = models.BooleanField("Acknowledged", default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        default_related_name = "event_notifications"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["savegame", "acknowledged"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} (Year {self.year})"
