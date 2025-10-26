from http import HTTPStatus

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from apps.edict.models import Edict
from apps.edict.selectors import get_available_edicts_for_savegame
from apps.edict.services.edict_activation import EdictActivationService
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class EdictListView(SavegameRequiredMixin, generic.TemplateView):
    """Display list of all edicts with availability status."""

    template_name = "edict/edict_list.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        context["edicts"] = get_available_edicts_for_savegame(savegame=savegame)

        return context


class EdictActivateView(SavegameRequiredMixin, generic.View):
    """Handle edict activation (POST only)."""

    http_method_names = ("post",)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        edict = get_object_or_404(Edict, pk=kwargs["pk"])

        # Process activation
        service = EdictActivationService(savegame=savegame, edict=edict)
        result = service.process()

        # Add message
        if result.success:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)

        # Return HTMX response to redirect back to edict list
        response = HttpResponse(status=HTTPStatus.OK)
        response["HX-Redirect"] = reverse("edict:edict-list-view")

        return response
