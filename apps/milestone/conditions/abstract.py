import abc

from apps.savegame.models import Savegame


class AbstractCondition(abc.ABC):
    """
    Abstract base class for milestone conditions.

    Subclasses must define:
    - VERBOSE_NAME: Human-readable name for the condition
    - is_valid(): Method to check if condition is met
    """

    VERBOSE_NAME: str = "Unknown Condition"

    savegame: Savegame
    value: int | str | float

    def __init__(self, *, savegame: Savegame, value: int | str | float) -> None:
        self.savegame = savegame
        self.value = value

    @abc.abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError

    @classmethod
    def get_verbose_name(cls) -> str:
        """Get the human-readable name for this condition type."""
        return cls.VERBOSE_NAME
