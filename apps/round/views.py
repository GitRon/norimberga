import json
from http import HTTPStatus

from django.contrib import messages
from django.http import HttpResponse
from django.views import generic

from apps.city.services.building.maintenance import BuildingMaintenanceService
from apps.city.services.building.population import BuildingPopulationService
from apps.event.services.selection import EventSelectionService


class RoundView(generic.View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        event = EventSelectionService().process()
        if event:
            message = event.process()
            messages.add_message(self.request, messages.INFO, message)

        # Regular round-based stuff
        BuildingMaintenanceService().process()
        BuildingPopulationService().process()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "updateNavbarValues": "-",
                "refreshMap": "-",
            }
        )
        return response
