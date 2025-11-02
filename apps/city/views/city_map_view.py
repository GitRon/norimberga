from django.views import generic


class CityMapView(generic.TemplateView):
    template_name = "city/partials/city/_city_map.html"
