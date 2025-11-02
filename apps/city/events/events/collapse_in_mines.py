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
    LEVEL = messages.WARNING
    TITLE = "⚒️ Collapse in the Mines"

    # Store the randomized effect values for each choice
    rescue_cost: int
    rescue_trust_gain: int
    seal_unrest_increase: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)

        # Pre-roll the random values so they're consistent
        self.rescue_cost = random.randint(50, 100)
        self.rescue_trust_gain = random.randint(5, 8)
        self.seal_unrest_increase = random.randint(10, 15)

    def get_verbose_text(self) -> str:
        return (
            "A section of your city's silver mine collapses, trapping workers inside. "
            "Rescue efforts would be costly and slow, but leaving them might spark outrage."
        )

    def get_choices(self) -> list[Choice]:
        return [
            Choice(
                label="Send rescuers immediately",
                description=(
                    f"Mount an immediate rescue operation to save the trapped miners. "
                    f"This will cost {self.rescue_cost} coins and halt mining operations temporarily, "
                    f"but the people will appreciate your commitment to their safety "
                    f"(-{self.rescue_trust_gain} unrest)."
                ),
                effects=[
                    DecreaseCoins(coins=self.rescue_cost),
                    DecreaseUnrestAbsolute(lost_unrest=self.rescue_trust_gain),
                ],
            ),
            Choice(
                label="Seal the tunnels",
                description=(
                    f"Order the dangerous tunnels sealed to prevent further collapse. "
                    f"Mining can resume quickly and no rescue costs are incurred, "
                    f"but the workers and their families will be outraged by the abandoned miners "
                    f"(+{self.seal_unrest_increase} unrest)."
                ),
                effects=[
                    IncreaseUnrestAbsolute(additional_unrest=self.seal_unrest_increase),
                ],
            ),
        ]
