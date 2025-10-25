from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from apps.savegame.models import Savegame


class SavegameRequiredMixin:
    """
    Mixin that redirects to the savegame list if the user doesn't have an active savegame.

    Use this mixin for views that require an active savegame to function.
    """

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:  # noqa: PBR001, PBR002
        if request.user.is_authenticated:
            savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
            if not savegame:
                return HttpResponseRedirect(reverse_lazy("savegame:savegame-list"))
        return super().dispatch(request, *args, **kwargs)
