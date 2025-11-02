import json
from http import HTTPStatus

from django.contrib import messages
from django.http import HttpResponse
from django.views import generic

from apps.event.models.event_choice import EventChoice
from apps.savegame.mixins.savegame import SavegameRequiredMixin


class EventChoiceSelectView(SavegameRequiredMixin, generic.View):
    """
    Handles the user's selection of a choice for a pending event.

    When a user selects a choice:
    1. Get the event instance
    2. Get the selected choice
    3. Apply the choice's effects
    4. Delete the EventChoice record
    5. Show a message to the user
    6. Redirect to next pending event or back to game
    """

    http_method_names = ("post",)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        from apps.savegame.models import Savegame

        savegame = Savegame.objects.filter(user=request.user, is_active=True).first()
        event_choice_id = kwargs.get("pk")
        choice_index = int(request.POST.get("choice_index", 0))

        try:
            event_choice = EventChoice.objects.get(pk=event_choice_id, savegame=savegame)
        except EventChoice.DoesNotExist:
            return HttpResponse("Event not found", status=HTTPStatus.NOT_FOUND)

        # Get the event instance and its choices
        event = event_choice.get_event_instance()
        choices = event.get_choices()

        # Validate choice index
        if choice_index < 0 or choice_index >= len(choices):
            return HttpResponse("Invalid choice", status=HTTPStatus.BAD_REQUEST)

        # Get the selected choice and apply its effects
        selected_choice = choices[choice_index]
        selected_choice.apply_effects(savegame=savegame)

        # Refresh savegame from database to get updated values
        savegame.refresh_from_db()

        # Show message to user
        message_text = f"{event.get_verbose_text()}\n\nYou chose: {selected_choice.label}"
        messages.add_message(request, event.LEVEL, message_text, extra_tags=event.TITLE)

        # Delete the event choice record
        event_choice.delete()

        # Check if there are more pending events
        has_more_pending = EventChoice.objects.filter(savegame=savegame).exists()

        # Prepare response with HTMX triggers
        response = HttpResponse(status=HTTPStatus.OK)
        triggers = {
            "reloadMessages": "-",
            "updateNavbarValues": "-",
            "refreshMap": "-",
        }

        # If there are more pending events, show the next one
        if has_more_pending:
            triggers["showPendingEvents"] = "-"

        response["HX-Trigger"] = json.dumps(triggers)
        return response
