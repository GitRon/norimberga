import json
from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Savegame, Tile


class CoinUpdateView(generic.DetailView):
    model = Savegame
    template_name = "savegame/partials/_coins.html"


class PopulationUpdateView(generic.DetailView):
    model = Savegame
    template_name = "savegame/partials/_population.html"


class LandingPageView(generic.TemplateView):
    template_name = "city/landing_page.html"


class CityMapView(generic.TemplateView):
    template_name = "city/partials/map/_city_map.html.html"


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
                "updateCoins": "-",
            }
        )
        return response

    def get_success_url(self):
        return None
