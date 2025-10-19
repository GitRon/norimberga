import random

from django.contrib import messages

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.event.events.events.base_event import BaseEvent
from apps.savegame.models import Savegame


class Event(BaseEvent):
    PROBABILITY = 60
    LEVEL = messages.INFO
    TITLE = "Protest"

    initial_population: int
    initial_coins: int
    lost_population: int
    lost_coins: int

    def __init__(self, *, savegame: Savegame):
        super().__init__(savegame=savegame)
        self.initial_population = self.savegame.population
        self.initial_coins = self.savegame.coins
        self.lost_population = random.randint(1, 5)
        self.lost_coins = random.randint(10, 30)

    def get_probability(self) -> int | float:
        if self.savegame.population > 0 and 25 <= self.savegame.unrest < 75:
            # Scale probability based on unrest level (0% at unrest 25, 100% at unrest 74)
            unrest_factor = (self.savegame.unrest - 25) / 50
            return super().get_probability() * unrest_factor
        return 0

    def _prepare_effect_decrease_population(self) -> DecreasePopulationAbsolute:
        return DecreasePopulationAbsolute(lost_population=self.lost_population)

    def _prepare_effect_decrease_coins(self) -> DecreaseCoins:
        return DecreaseCoins(coins=self.lost_coins)

    def get_verbose_text(self) -> str:
        self.savegame.refresh_from_db()
        population_loss = self.initial_population - self.savegame.population
        coins_loss = self.initial_coins - self.savegame.coins

        message = (
            f"Citizens gathered in the streets to protest against the city council. "
            f"The protest turned violent, resulting in {population_loss} casualties"
        )

        if coins_loss > 0:
            message += f" and {coins_loss} coins looted by the protesters"

        message += "."
        return message
