from django.views import generic

from apps.savegame.models import Savegame


class SavegameListView(generic.ListView):
    model = Savegame
    template_name = "savegame/savegame_list.html"
    context_object_name = "savegames"

    def get_queryset(self) -> list[Savegame]:
        return Savegame.objects.filter(user=self.request.user).order_by("-id")
