from apps.city.models import Savegame


class IncreaseCoins:
    coins: int

    def __init__(self, coins: int):
        self.coins = coins

    def process(self):
        savegame, _ = Savegame.objects.get_or_create(id=1)
        savegame.coins += self.coins
        savegame.save()
