from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from apps.event.models import EventNotification
from apps.savegame.mixins.savegame import SavegameRequiredMixin
from apps.savegame.models import Savegame


class NotificationBoardView(SavegameRequiredMixin, generic.TemplateView):
    """
    Display one notification at a time for the current savegame.
    Shows the first unacknowledged notification.
    """

    template_name = "event/notification_board.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()

        if savegame:
            # Get the first unacknowledged notification
            notification = savegame.event_notifications.filter(acknowledged=False).first()

            # Count total unacknowledged notifications
            total_notifications = savegame.event_notifications.filter(acknowledged=False).count()

            context["notification"] = notification
            context["total_notifications"] = total_notifications

        return context


class NotificationAcknowledgeView(SavegameRequiredMixin, generic.View):
    """
    HTMX endpoint to acknowledge a notification.
    After acknowledgment, either shows the next notification or redirects to city view.
    """

    http_method_names = ("post",)

    def post(self, request, pk, *args, **kwargs) -> HttpResponse:
        savegame = Savegame.objects.filter(user=self.request.user, is_active=True).first()
        if not savegame:
            return HttpResponse("No active savegame found", status=400)

        # Get and acknowledge the notification
        notification = get_object_or_404(EventNotification, pk=pk, savegame=savegame)
        notification.acknowledged = True
        notification.save()

        # Check if there are more unacknowledged notifications
        next_notification = savegame.event_notifications.filter(acknowledged=False).first()

        if next_notification:
            # Redirect to notification board to show next notification
            response = HttpResponse(status=200)
            response["HX-Redirect"] = reverse("event:notification-board")
            return response

        # No more notifications, redirect to city view
        response = HttpResponse(status=200)
        response["HX-Redirect"] = reverse("city:landing-page")
        return response
