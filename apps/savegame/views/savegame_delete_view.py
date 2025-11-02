from http import HTTPStatus

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from apps.savegame.models import Savegame


class SavegameDeleteView(generic.DeleteView):
    model = Savegame
    success_url = reverse_lazy("savegame:savegame-list")

    def get_queryset(self) -> list[Savegame]:
        # Only allow deleting own savegames that are not active
        return Savegame.objects.filter(user=self.request.user, is_active=False)

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        # If HTMX request, return empty response for client-side removal
        if request.headers.get("HX-Request"):
            return HttpResponse(status=HTTPStatus.OK)

        # Otherwise redirect to list view
        return HttpResponseRedirect(self.get_success_url())
