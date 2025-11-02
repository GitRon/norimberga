from apps.event.models.event_choice import EventChoice


class EventChoiceStorageService:
    """
    Service for storing events with user choices to the database.

    When an event requires user interaction, we store it as an EventChoice
    record so the user can be presented with options later.
    """

    def __init__(self, *, savegame):
        self.savegame = savegame

    def _get_module_path(self, *, event) -> str:
        """Extract the module path from an event instance."""
        return event.__class__.__module__

    def _get_class_name(self, *, event) -> str:
        """Extract the class name from an event instance."""
        return event.__class__.__name__

    def _store_event(self, *, event) -> EventChoice:
        """Store a single event in the database."""
        return EventChoice.objects.create(
            savegame=self.savegame,
            event_module=self._get_module_path(event=event),
            event_class_name=self._get_class_name(event=event),
        )

    def process(self, *, events: list) -> list[EventChoice]:
        """
        Store multiple events with choices to the database.

        Args:
            events: List of event instances that have choices

        Returns:
            List of created EventChoice records
        """
        return [self._store_event(event=event) for event in events if event.has_choices()]
