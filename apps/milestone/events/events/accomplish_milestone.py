from django.contrib import messages

from apps.city.models import Savegame
from apps.event.events.events.base_event import BaseEvent
from apps.milestone.events.effects.milestone.accomplish_milestone import AccomplishMilestone
from apps.milestone.milestones.grow_city import GrowCityMilestone


class Event(BaseEvent):
    PROBABILITY = 0
    LEVEL = messages.SUCCESS
    TITLE = "Milestone accomplished"

    savegame: Savegame
    accomplish_milestones: list = []

    def __init__(self):
        super().__init__()
        self.savegame, _ = Savegame.objects.get_or_create(id=1)

        # TODO(RV): build service to get active milestones
        active_milestones = [GrowCityMilestone(savegame_id=self.savegame.id)]
        self.PROBABILITY = 0
        for milestone in active_milestones:
            if milestone.is_accomplished():
                self.accomplish_milestones.append(milestone)
                self.PROBABILITY = 100

    def get_probability(self):
        return self.PROBABILITY

    def _prepare_effect_accomplish_milestone(self):
        # For now, only one milestone per round can be accomplished
        for milestone in self.accomplish_milestones:
            return AccomplishMilestone(
                # TODO(RV): store a nice string in the database
                savegame_id=self.savegame.id,
                milestone=str(milestone),
                current_year=self.savegame.current_year,
            )

    def get_verbose_text(self):
        # TODO(RV): make this more pretty
        milestone_str = ", ".join(str(milestone) for milestone in self.accomplish_milestones).strip()
        return (
            f'Your prosperous city has accomplished a new milestone! Rejoice that "{milestone_str}" has been achieved.'
        )
