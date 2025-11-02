from django.views import generic


class NavbarValuesView(generic.TemplateView):
    template_name = "partials/_navbar_values.html"
