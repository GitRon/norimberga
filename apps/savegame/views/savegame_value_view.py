from django.views import generic

from apps.savegame.models import Savegame


class SavegameValueView(generic.DetailView):
    model = Savegame
    template_name = "savegame/partials/_nav_values.html"
