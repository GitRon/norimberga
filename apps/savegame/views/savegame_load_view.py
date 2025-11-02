from http import HTTPStatus

from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic

from apps.savegame.models import Savegame


class SavegameLoadView(generic.View):
    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.get(pk=pk, user=request.user)

        # Set all other savegames of this user to inactive
        Savegame.objects.filter(user=request.user).update(is_active=False)

        # Set this savegame to active
        savegame.is_active = True
        savegame.save()

        return HttpResponse(status=HTTPStatus.OK, headers={"HX-Redirect": reverse_lazy("city:landing-page")})
