import inspect

from django.contrib import messages


class BaseEvent:
    """
    Prefix every method to instantiate a new event effect with "_prepare_effect"
    """

    PROBABILITY = 0
    LEVEL = messages.INFO
    TITLE = "Missing title"

    def __init__(self, *, savegame):
        self.savegame = savegame

    def get_probability(self) -> int | float:
        return self.PROBABILITY

    def get_effects(self) -> list:
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        return [getattr(self, method[0])() for method in methods if method[0].startswith("_prepare_effect")]

    def get_verbose_text(self):
        raise NotImplementedError

    def get_choices(self) -> list | None:
        """
        Return a list of Choice instances if this event requires user interaction.
        Return None if this event should auto-apply effects (default behavior).

        Override this method in subclasses that need user choices.
        """
        return None

    def has_choices(self) -> bool:
        """Check if this event requires user interaction."""
        return self.get_choices() is not None

    def process(self) -> str:
        for effect in self.get_effects():
            if effect is not None:
                effect.process(savegame=self.savegame)

        return self.get_verbose_text()
