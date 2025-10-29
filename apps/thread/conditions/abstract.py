import abc

from apps.savegame.models import Savegame


class AbstractThreadCondition(abc.ABC):
    """
    Abstract base class for thread conditions.

    Subclasses must define:
    - VERBOSE_NAME: Human-readable name for the condition
    - is_active(): Method to check if thread condition is met
    - get_intensity(): Method to calculate how severe the thread is
    """

    VERBOSE_NAME: str = "Unknown Thread"

    savegame: Savegame

    def __init__(self, *, savegame: Savegame) -> None:
        self.savegame = savegame

    @abc.abstractmethod
    def is_active(self) -> bool:
        """Check if the thread condition is currently met."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_intensity(self) -> int:
        """Calculate the intensity/severity of the thread."""
        raise NotImplementedError

    @classmethod
    def get_verbose_name(cls) -> str:
        """Get the human-readable name for this thread type."""
        return cls.VERBOSE_NAME
