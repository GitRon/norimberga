from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Terrain(models.Model):
    """
    Type of country. Determines what you can build on it.
    """

    name = models.CharField(max_length=50)
    image_filename = models.CharField(
        max_length=100,
        default="default.png",
        help_text="Filename of the terrain image in static/img/tiles/. Example: 'grass.png'",
    )
    probability = models.PositiveSmallIntegerField(
        "Probability weight", validators=(MaxValueValidator(100), MinValueValidator(1))
    )
    is_water = models.BooleanField("Is water", default=False)

    class Meta:
        default_related_name = "terrains"

    def __str__(self) -> str:
        return self.name
