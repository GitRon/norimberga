import abc

from apps.city.models import Savegame


class AbstractCondition(abc.ABC):
    savegame_id: int

    @abc.abstractmethod
    def is_valid(self, *, savegame: Savegame) -> bool:
        raise NotImplementedError
