from django.views import generic


class CityMessagesView(generic.TemplateView):
    template_name = "city/partials/city/_messages.html"
