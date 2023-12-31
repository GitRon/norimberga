import inspect

from django.contrib import messages


class BaseEvent:
    """
    Prefix every method to instantiate a new event effect with "_prepare_effect"
    """

    PROBABILITY = 0
    LEVEL = messages.INFO
    TITLE = "Missing title"

    def get_probability(self):
        return self.PROBABILITY

    def get_effects(self):
        method_list = inspect.getmembers(self, predicate=inspect.ismethod)
        return [getattr(self, method[0])() for method in method_list if method[0].startswith("_prepare_effect")]

    def get_verbose_text(self):
        raise NotImplementedError

    def process(self) -> str:
        for effect in self.get_effects():
            if effect is not None:
                effect.process()

        return self.get_verbose_text()
