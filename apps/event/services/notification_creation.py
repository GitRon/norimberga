from django.contrib import messages as django_messages

from apps.event.events.events.base_event import BaseEvent
from apps.event.models import EventNotification
from apps.savegame.models import Savegame


class NotificationCreationService:
    """
    Creates persistent EventNotification records from selected events.
    Processes each event (runs effects) and stores the results.
    """

    # Map Django message levels to EventNotification.Level choices
    LEVEL_MAPPING = {
        django_messages.INFO: EventNotification.Level.INFO,
        django_messages.SUCCESS: EventNotification.Level.SUCCESS,
        django_messages.WARNING: EventNotification.Level.WARNING,
        django_messages.ERROR: EventNotification.Level.ERROR,
    }

    def __init__(self, *, savegame: Savegame, events: list[BaseEvent]):
        self.savegame = savegame
        self.events = events

    def _get_level_choice(self, *, django_level: int) -> str:
        """Convert Django message level to EventNotification.Level choice."""
        return self.LEVEL_MAPPING.get(django_level, EventNotification.Level.INFO)

    def process(self) -> list[EventNotification]:
        """Process all events and create notification records."""
        notifications = []

        for event in self.events:
            # Process the event (runs all effects and returns verbose text)
            message = event.process()

            # Skip events that don't return a message
            if not message:
                continue

            # Create notification record
            notification = EventNotification.objects.create(
                savegame=self.savegame,
                year=self.savegame.current_year,
                title=event.TITLE,
                message=message,
                level=self._get_level_choice(django_level=event.LEVEL),
                acknowledged=False,
            )
            notifications.append(notification)

        return notifications
