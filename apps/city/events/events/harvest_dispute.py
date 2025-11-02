import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_unrest_absolute import DecreaseUnrestAbsolute
from apps.city.events.effects.savegame.increase_unrest_absolute import IncreaseUnrestAbsolute
from apps.event.events.choice import Choice
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 3
    LEVEL = messages.INFO
    TITLE = "🌾 The Harvest Dispute"

    # Store the randomized effect values for each choice
    investigation_cost: int
    investigation_unrest_decrease: int
    arbitrary_unrest_increase: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)

        # Pre-roll the random values so they're consistent
        self.investigation_cost = random.randint(20, 40)
        self.investigation_unrest_decrease = random.randint(3, 6)
        self.arbitrary_unrest_increase = random.randint(5, 10)

    def get_verbose_text(self) -> str:
        return (
            "Two neighboring farmers accuse each other of stealing grain from a shared field. "
            "The village court can't decide and turns to you for judgment."
        )

    def get_choices(self) -> list[Choice]:
        return [
            Choice(
                label="Conduct a thorough investigation",
                description=(
                    f"Send officials to investigate the dispute fairly and gather evidence. "
                    f"This will cost {self.investigation_cost} coins for the investigation, "
                    f"but your commitment to justice will be appreciated by all farmers "
                    f"(-{self.investigation_unrest_decrease} unrest)."
                ),
                effects=[
                    DecreaseCoins(coins=self.investigation_cost),
                    DecreaseUnrestAbsolute(lost_unrest=self.investigation_unrest_decrease),
                ],
            ),
            Choice(
                label="Make an arbitrary ruling",
                description=(
                    f"Quickly rule in favor of one farmer without investigation to save time and resources. "
                    f"While this costs nothing, the losing farmer and his supporters will feel the judgment "
                    f"was unjust, causing resentment among the farming community "
                    f"(+{self.arbitrary_unrest_increase} unrest)."
                ),
                effects=[
                    IncreaseUnrestAbsolute(additional_unrest=self.arbitrary_unrest_increase),
                ],
            ),
        ]
