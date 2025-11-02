import factory

from apps.event.events.choice import Choice
from apps.event.events.events.base_event import BaseEvent
from apps.event.models.event_choice import EventChoice
from apps.savegame.tests.factories import SavegameFactory


class EventChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventChoice

    savegame = factory.SubFactory(SavegameFactory)
    event_module = "apps.event.tests.factories"
    event_class_name = "MockEventWithChoices"


class MockEvent(BaseEvent):
    """Mock event class for testing purposes."""

    PROBABILITY = 50
    TITLE = "Mock Event"

    def __init__(self, *, savegame, probability=None):
        super().__init__(savegame=savegame)
        if probability is not None:
            self.PROBABILITY = probability

    def get_verbose_text(self):
        return "Mock event occurred"


class HighProbabilityEvent(BaseEvent):
    """Event with high probability for testing."""

    PROBABILITY = 90
    TITLE = "High Probability Event"

    def __init__(self, *, savegame):
        super().__init__(savegame=savegame)

    def get_verbose_text(self):
        return "High probability event occurred"


class LowProbabilityEvent(BaseEvent):
    """Event with low probability for testing."""

    PROBABILITY = 10
    TITLE = "Low Probability Event"

    def __init__(self, *, savegame):
        super().__init__(savegame=savegame)

    def get_verbose_text(self):
        return "Low probability event occurred"


class ZeroProbabilityEvent(BaseEvent):
    """Event with zero probability for testing."""

    PROBABILITY = 0
    TITLE = "Zero Probability Event"

    def __init__(self, *, savegame):
        super().__init__(savegame=savegame)

    def get_verbose_text(self):
        return "Zero probability event occurred"


class MockEventWithChoices(BaseEvent):
    """Mock event with choices for testing the choice system."""

    PROBABILITY = 50
    TITLE = "Mock Event With Choices"

    def __init__(self, *, savegame):
        super().__init__(savegame=savegame)

    def get_verbose_text(self):
        return "Mock event with choices occurred"

    def get_choices(self) -> list[Choice]:
        from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
        from apps.city.events.effects.savegame.increase_coins import IncreaseCoins

        return [
            Choice(
                label="Good choice",
                description="This is the good choice that gives you coins",
                effects=[IncreaseCoins(coins=100)],
            ),
            Choice(
                label="Bad choice",
                description="This is the bad choice that takes coins",
                effects=[DecreaseCoins(coins=50)],
            ),
        ]
