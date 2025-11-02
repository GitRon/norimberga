import json
from http import HTTPStatus

from django.contrib import messages
from django.http import HttpResponse
from django.views import generic

from apps.city.services.wall.enclosure import WallEnclosureService
from apps.event.services.selection import EventSelectionService
from apps.event.services.storage import EventChoiceStorageService
from apps.savegame.models import Savegame


class RoundView(generic.View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if not savegame:
            return HttpResponse("No active savegame found", status=400)

        # Increment the year
        savegame.current_year += 1
        savegame.save()

        events = EventSelectionService(savegame=savegame).process()

        # Separate events with choices from those without
        events_with_choices = [event for event in events if event.has_choices()]
        events_without_choices = [event for event in events if not event.has_choices()]

        # Store events with choices for user interaction
        if events_with_choices:
            EventChoiceStorageService(savegame=savegame).process(events=events_with_choices)

        # Process events without choices immediately (existing behavior)
        for event in events_without_choices:
            message = event.process()
            messages.add_message(self.request, event.LEVEL, message, extra_tags=event.TITLE)

        # Show "quiet year" message only if no events at all
        if not len(events):
            messages.add_message(
                self.request, messages.INFO, "It was a quiet year. Nothing happened out of the ordinary."
            )

        # Update enclosure status after events (in case buildings were removed)
        savegame.is_enclosed = WallEnclosureService(savegame=savegame).process()
        savegame.save()

        response = HttpResponse(status=HTTPStatus.OK)
        triggers = {
            "reloadMessages": "-",
            "refreshMap": "-",
            "updateNavbarValues": "-",
        }

        # Add trigger to show pending events if any were stored
        if events_with_choices:
            triggers["showPendingEvents"] = "-"

        response["HX-Trigger"] = json.dumps(triggers)
        return response
