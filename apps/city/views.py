from http import HTTPStatus

from django.http import HttpResponse
from django.views import generic

from apps.city.forms.tile import TileBuildingForm
from apps.city.models import Savegame, Tile


class LandingPageView(generic.TemplateView):
    template_name = "city/landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["savegame"], _ = Savegame.objects.get_or_create(id=1)

        return context


class CityMapView(generic.TemplateView):
    template_name = "city/partials/map/_city_map.html.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["savegame"], _ = Savegame.objects.get_or_create(id=1)

        return context


class TileBuildView(generic.UpdateView):
    model = Tile
    form_class = TileBuildingForm
    template_name = "city/partials/tile/update_tile.html"

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form=form)
        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Trigger"] = "refreshMap"
        return response

    def get_success_url(self):
        return None

    def form_invalid(self, form):
        # We return a 400 because the form is supposed to be always valid (all-optional fields)
        return HttpResponse(status=HTTPStatus.BAD_REQUEST)
