from django.shortcuts import render
from django.views import generic

from apps.city.models import Savegame


class CityMapView(generic.TemplateView):
    template_name = "city/city_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['savegame'], _ = Savegame.objects.get_or_create(id=1)

        return context
