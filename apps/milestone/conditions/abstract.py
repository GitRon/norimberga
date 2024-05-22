from apps.city.models import Savegame


class AbstractCondition:
    savegame_id: int

    def __init__(self, **kwargs) -> None:
        pass

    def is_valid(self, savegame: Savegame) -> bool:
        raise NotImplementedError
