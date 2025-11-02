from django.views import generic

from apps.savegame.mixins.savegame import SavegameRequiredMixin


class LandingPageView(SavegameRequiredMixin, generic.TemplateView):
    template_name = "city/landing_page.html"
