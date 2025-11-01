import json
from http import HTTPStatus

from django.http import HttpResponse
from django.urls import reverse
from django.views import generic

from apps.city.services.wall.enclosure import WallEnclosureService
from apps.event.services.notification_creation import NotificationCreationService
from apps.event.services.selection import EventSelectionService
from apps.savegame.models import Savegame


class RoundView(generic.View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        if not savegame:
            return HttpResponse("No active savegame found", status=400)

        # Check for unacknowledged notifications - prevent round progression
        has_unacknowledged = savegame.event_notifications.filter(acknowledged=False).exists()
        if has_unacknowledged:
            return HttpResponse("Please acknowledge all notifications before finishing the round", status=400)

        # Increment the year
        savegame.current_year += 1
        savegame.save()

        # Select events that should occur this round
        events = EventSelectionService(savegame=savegame).process()

        # Create persistent notifications from events
        if events:
            NotificationCreationService(savegame=savegame, events=events).process()

        # Update enclosure status after events (in case buildings were removed)
        savegame.is_enclosed = WallEnclosureService(savegame=savegame).process()
        savegame.save()

        # Check if there are unacknowledged notifications
        has_notifications = savegame.event_notifications.filter(acknowledged=False).exists()

        response = HttpResponse(status=HTTPStatus.OK)

        if has_notifications:
            # Redirect to notification board
            response["HX-Redirect"] = reverse("event:notification-board")
        else:
            # No notifications, just refresh the UI
            response["HX-Trigger"] = json.dumps(
                {
                    "refreshMap": "-",
                    "updateNavbarValues": "-",
                }
            )

        return response
