import typing

from django.db import models

if typing.TYPE_CHECKING:
    from apps.event.models import EventNotification
    from apps.savegame.models import Savegame


class EventNotificationManager(models.Manager):
    def create_notification(
        self,
        *,
        savegame: "Savegame",
        year: int,
        title: str,
        message: str,
    ) -> "EventNotification":
        return self.create(
            savegame=savegame,
            year=year,
            title=title,
            message=message,
            acknowledged=False,
        )
