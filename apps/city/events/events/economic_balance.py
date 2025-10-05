from django.contrib import messages

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.models import Savegame
from apps.city.selectors.savegame import get_balance_data
from apps.event.events.events.base_event import BaseEvent


class Event(BaseEvent):
    PROBABILITY = 100
    LEVEL = messages.INFO
    TITLE = "Economic Balance"

    balance: int
    taxes: int
    maintenance: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        balance_data = get_balance_data(savegame=savegame)
        self.balance = balance_data["balance"]
        self.taxes = balance_data["taxes"]
        self.maintenance = balance_data["maintenance"]

    def get_probability(self) -> int | float:
        # Only trigger if there's a non-zero balance
        return super().get_probability() if self.balance != 0 else 0

    def _prepare_effect_adjust_coins(self) -> IncreaseCoins | DecreaseCoins | None:
        if self.balance > 0:
            return IncreaseCoins(coins=self.balance)
        elif self.balance < 0:
            return DecreaseCoins(coins=abs(self.balance))
        return None

    def get_verbose_text(self) -> str:
        if self.balance > 0:
            return (
                f"Tax collection brought in {self.taxes} coins while building maintenance "
                f"cost {self.maintenance} coins. The city treasury gained {self.balance} coins."
            )
        else:
            return (
                f"Tax collection brought in {self.taxes} coins while building maintenance "
                f"cost {self.maintenance} coins. The city treasury lost {abs(self.balance)} coins."
            )
