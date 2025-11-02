from typing import TYPE_CHECKING

from django.views import generic

from apps.event.models.event_choice import EventChoice
from apps.savegame.mixins.savegame import SavegameRequiredMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet


class PendingEventsView(SavegameRequiredMixin, generic.ListView):
    """
    Displays the list of pending events that require user interaction.
    """

    model = EventChoice
    template_name = "event/partials/_pending_events.html"
    context_object_name = "pending_events"

    def get_queryset(self) -> "QuerySet[EventChoice]":
        """Get all pending events for the active savegame."""
        from apps.savegame.models import Savegame

        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        return EventChoice.objects.filter(savegame=savegame)
