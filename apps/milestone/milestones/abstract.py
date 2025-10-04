import abc
from typing import Self

from apps.city.models import Savegame
from apps.milestone.conditions.abstract import AbstractCondition


class AbstractMilestone(abc.ABC):
    savegame: Savegame

    conditions: tuple[AbstractCondition] = ()

    previous_quests: tuple[Self] = ()
    next_quests: tuple[Self] = ()

    def __init__(self, *, savegame_id: int) -> None:
        self.savegame = Savegame.objects.get(id=savegame_id)

    def is_accomplished(self) -> bool:
        return all(condition.is_valid(savegame=self.savegame) for condition in self.conditions)
