from django.views import generic

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
