import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.event.events.choice import Choice
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 3
    LEVEL = messages.INFO
    TITLE = "🏛️ The Wandering Preacher"

    # Store the randomized effect values for each choice
    grant_permission_decrease: int
    grant_permission_risk: int
    silence_unrest_increase: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)

        # Pre-roll the random values so they're consistent
        self.grant_permission_decrease = random.randint(5, 10)
        self.grant_permission_risk = random.randint(3, 7)
        self.silence_unrest_increase = random.randint(3, 5)

    def get_verbose_text(self) -> str:
        return (
            "A charismatic preacher arrives at the city gates, drawing large crowds in the marketplace. "
            "His sermons inspire hope — but also question your rule."
        )

    def get_choices(self) -> list[Choice]:
        return [
            Choice(
                label="Grant him permission to speak",
                description=(
                    f"The preacher's words inspire hope and calm tensions among the people "
                    f"(-{self.grant_permission_decrease} unrest). However, his rhetoric may also "
                    f"sow seeds of discontent if his message turns against you "
                    f"(+{self.grant_permission_risk} unrest risk)."
                ),
                effects=[
                    DecreaseUnrestAbsolute(lost_unrest=self.grant_permission_decrease),
                    IncreaseUnrestAbsolute(additional_unrest=self.grant_permission_risk),
                ],
            ),
            Choice(
                label="Silence him quietly",
                description=(
                    f"You prevent the preacher from speaking, maintaining order and your authority. "
                    f"However, word spreads of your heavy-handed approach, causing some discontent "
                    f"among the faithful (+{self.silence_unrest_increase} unrest)."
                ),
                effects=[
                    IncreaseUnrestAbsolute(additional_unrest=self.silence_unrest_increase),
                ],
            ),
        ]
