from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.services.building.maintenance import BuildingMaintenanceService
from apps.city.services.building.population import BuildingPopulationService
from apps.event.services.event import EventService


class RoundView(generic.View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        BuildingMaintenanceService().process()
        BuildingPopulationService().process()
        EventService().process()
        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = "updateNavbarValues"
        return response
