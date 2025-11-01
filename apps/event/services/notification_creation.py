from apps.event.events.events.base_event import BaseEvent
from apps.event.models import EventNotification
from apps.savegame.models import Savegame


class NotificationCreationService:
    """
    Creates persistent EventNotification records from selected events.
    Processes each event (runs effects) and stores the results.
    """

    def __init__(self, *, savegame: Savegame, events: list[BaseEvent]):
        self.savegame = savegame
        self.events = events

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
                acknowledged=False,
            )
            notifications.append(notification)

        return notifications
