import json
from http import HTTPStatus

from django.contrib import messages
from django.http import HttpResponse
from django.views import generic

from apps.event.services.selection import EventSelectionService


class RoundView(generic.View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        events = EventSelectionService().process()
        for event in events:
            message = event.process()
            messages.add_message(self.request, event.LEVEL, message, extra_tags=event.TITLE)

        if not len(events):
            messages.add_message(
                self.request, messages.INFO, "It was a quiet year. Nothing happened out of the ordinary."
            )

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "reloadMessages": "-",
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response
