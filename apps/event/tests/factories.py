from apps.event.events.events.base_event import BaseEvent


class MockEvent(BaseEvent):
    """Mock event class for testing purposes."""

    PROBABILITY = 50
    TITLE = "Mock Event"

    def __init__(self, probability=None):
        super().__init__()
        if probability is not None:
            self.PROBABILITY = probability

    def get_verbose_text(self):
        return "Mock event occurred"


class HighProbabilityEvent(BaseEvent):
    """Event with high probability for testing."""

    PROBABILITY = 90
    TITLE = "High Probability Event"

    def get_verbose_text(self):
        return "High probability event occurred"


class LowProbabilityEvent(BaseEvent):
    """Event with low probability for testing."""

    PROBABILITY = 10
    TITLE = "Low Probability Event"

    def get_verbose_text(self):
        return "Low probability event occurred"


class ZeroProbabilityEvent(BaseEvent):
    """Event with zero probability for testing."""

    PROBABILITY = 0
    TITLE = "Zero Probability Event"

    def get_verbose_text(self):
        return "Zero probability event occurred"
