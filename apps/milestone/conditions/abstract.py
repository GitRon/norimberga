import abc

from apps.city.models import Savegame


class AbstractCondition(abc.ABC):
    savegame: Savegame
    value: int | str | float

    def __init__(self, *, savegame: Savegame, value: int | str | float) -> None:
        self.savegame = savegame
        self.value = value

    @abc.abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError
