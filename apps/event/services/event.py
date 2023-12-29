import random

from apps.event.models import Event


class EventService:
    def process(self) -> Event | None:
        dice = random.randint(0, 100)

        picked_event = Event.objects.filter(probability__gte=dice).first()

        if picked_event:
            picked_event.execute()

        return picked_event
