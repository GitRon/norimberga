import json
from http import HTTPStatus

from django.contrib import messages
from django.http import HttpResponse
from django.views import generic

from apps.city.services.wall.enclosure import WallEnclosureService
from apps.event.services.selection import EventSelectionService
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
        for event in events:
            message = event.process()
            messages.add_message(self.request, event.LEVEL, message, extra_tags=event.TITLE)

        if not len(events):
            messages.add_message(
                self.request, messages.INFO, "It was a quiet year. Nothing happened out of the ordinary."
            )

        # Update enclosure status after events (in case buildings were removed)
        savegame.is_enclosed = WallEnclosureService(savegame=savegame).process()
        savegame.save()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "reloadMessages": "-",
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response
