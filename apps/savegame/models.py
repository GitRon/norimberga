from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.savegame.managers.savegame import SavegameManager


class Savegame(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)
    coins = models.SmallIntegerField("Coins", default=1000)
    population = models.PositiveSmallIntegerField("Population", default=0)
    unrest = models.PositiveSmallIntegerField(
        "Unrest", default=0, validators=(MinValueValidator(0), MaxValueValidator(100))
    )
    current_year = models.PositiveSmallIntegerField("Current year", default=1150)
    coat_of_arms = models.ImageField("Coat of Arms", upload_to="coat_of_arms/", blank=True, null=True)

    is_active = models.BooleanField("Is active", default=False)
    is_enclosed = models.BooleanField("Is enclosed by wall", default=False)

    objects = SavegameManager()

    class Meta:
        default_related_name = "savegames"

    def __str__(self) -> str:
        return self.city_name
