import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Savegame, Tile
from apps.city.services.building.housing import BuildingHousingService


class SavegameValueView(generic.DetailView):
    model = Savegame
    template_name = "savegame/partials/_nav_values.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["max_housing_space"] = BuildingHousingService().calculate_max_space()
        return context


class LandingPageView(generic.TemplateView):
    template_name = "city/landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO(RV): move to context processor
        context["max_housing_space"] = BuildingHousingService().calculate_max_space()
        return context


class CityMapView(generic.TemplateView):
    template_name = "city/partials/city/_city_map.html"


class CityMessagesView(generic.TemplateView):
    template_name = "city/partials/city/_messages.html"


class TileBuildView(generic.UpdateView):
    model = Tile
    form_class = TileBuildingForm
    template_name = "city/partials/tile/update_tile.html"

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["savegame"], _ = Savegame.objects.get_or_create(id=1)
        return kwargs

    def form_valid(self, form):
        super().form_valid(form=form)

        if form.cleaned_data["building"]:
            savegame, _ = Savegame.objects.get_or_create(id=1)
            savegame.coins -= form.cleaned_data["building"].building_costs
            savegame.save()

        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = json.dumps(
            {
                "refreshMap": "-",
                "updateNavbarValues": "-",
            }
        )
        return response

    def get_success_url(self):
        return None
