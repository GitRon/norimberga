from apps.savegame.models import Savegame


class DecreaseCoins:
    coins: int

    def __init__(self, *, coins: int):
        self.coins = coins

    def process(self, *, savegame: Savegame):
        savegame.coins -= self.coins
        savegame.save()
