import importlib
from typing import Any

from django.db import models

from apps.savegame.models.savegame import Savegame


class EventChoice(models.Model):
    """
    Stores events that require user interaction (choices) before their effects can be applied.

    When an event has choices, instead of auto-applying effects, we:
    1. Create an EventChoice record in the database
    2. Display the event to the user with choice options
    3. Apply effects based on the user's selected choice
    4. Delete the EventChoice record
    """

    savegame = models.ForeignKey(Savegame, on_delete=models.CASCADE)
    event_module = models.CharField(
        max_length=255,
        help_text="Python module path (e.g., 'apps.city.events.events.wandering_preacher')",
    )
    event_class_name = models.CharField(
        max_length=100,
        default="Event",
        help_text="Class name within the module (usually 'Event')",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = "event_choices"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"EventChoice for {self.savegame.city_name}: {self.event_module}"

    def get_event_instance(self) -> Any:
        """
        Dynamically import and instantiate the event class.

        Returns:
            An instance of the event class with the savegame injected.
        """
        module = importlib.import_module(self.event_module)
        event_class = getattr(module, self.event_class_name)
        return event_class(savegame=self.savegame)

    def get_choices(self) -> list:
        """Get the choices available for this event."""
        event = self.get_event_instance()
        return event.get_choices()

    def get_title(self) -> str:
        """Get the event title."""
        event = self.get_event_instance()
        return event.TITLE

    def get_verbose_text(self) -> str:
        """Get the event description."""
        event = self.get_event_instance()
        return event.get_verbose_text()

    def get_level(self) -> int:
        """Get the message level for this event."""
        event = self.get_event_instance()
        return event.LEVEL
