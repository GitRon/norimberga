import random

from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class EventEffect(models.Model):
    class SignChoices(models.IntegerChoices):
        POSITIVE = 1, "Addition"
        NEGATIVE = 2, "Subtraction"

    class MethodChoices(models.IntegerChoices):
        ABSOLUTE = 1, "Absolute"
        RELATIVE = 2, "Relative"

    name = models.CharField("Name", max_length=75)
    content_type = models.ForeignKey(ContentType, verbose_name="Content type", on_delete=models.CASCADE)
    attribute = models.CharField("Attribute", max_length=100)
    min_amount = models.PositiveSmallIntegerField("Min. Amount")
    max_amount = models.PositiveSmallIntegerField("Max. Amount")
    sign = models.PositiveSmallIntegerField("Sign", choices=SignChoices.choices)
    method = models.PositiveSmallIntegerField("Method", choices=MethodChoices.choices)

    class Meta:
        default_related_name = "event_effects"

    def __str__(self):
        return self.name

    @property
    def amount(self):
        return random.randint(self.min_amount, self.max_amount)

    def get_filters_as_dict(self) -> dict:
        filter_dict = {}
        for effect_filter in self.effect_filters:
            filter_dict.update({effect_filter.attribute: effect_filter.value})
        return filter_dict


class EventEffectFilter(models.Model):
    effect = models.ForeignKey(EventEffect, verbose_name="Event effect", on_delete=models.CASCADE)
    attribute = models.CharField("Attribute", max_length=75)
    value = models.CharField("Value", max_length=75)

    class Meta:
        default_related_name = "effect_filters"

    def __str__(self):
        return self.attribute


class Event(models.Model):
    name = models.CharField("Name", max_length=100)
    text = models.TextField("Text")
    effects = models.ManyToManyField(EventEffect, verbose_name="Effect")
    probability = models.PositiveSmallIntegerField(
        "Probability", validators=(MinValueValidator(1), MaxValueValidator(100))
    )

    class Meta:
        default_related_name = "events"

    def __str__(self):
        return self.name

    def execute(self):
        effect: EventEffect
        for effect in self.effects.all():
            target_model = effect.content_type.model_class()
            # TODO(RV): filter for savegame (not so easy because of dynamic model)
            #  -> overwrite manager for savegame filter?
            target_instance = target_model.objects.filter(**effect.get_filters_as_dict()).first()

            if target_instance:
                # TODO(RV): case einbauen, wenn das feld ein FK ist - effekt 0 heißt, die verbindung wird gekappt?
                current_value = getattr(target_instance, effect.attribute)
                new_value = None

                if effect.sign == EventEffect.MethodChoices.ABSOLUTE:
                    if effect.sign == EventEffect.SignChoices.POSITIVE:
                        new_value = current_value + effect.amount
                    elif effect.sign == EventEffect.SignChoices.NEGATIVE:
                        new_value = current_value - effect.amount
                elif effect.sign == EventEffect.MethodChoices.RELATIVE:
                    if effect.sign == EventEffect.SignChoices.POSITIVE:
                        new_value = current_value * (1 + effect.amount)
                    elif effect.sign == EventEffect.SignChoices.NEGATIVE:
                        new_value = current_value * (1 - effect.amount)

                if new_value is None:
                    raise RuntimeError("Invalid event effect configuration")

                # TODO(RV): what if we increase population > capacity of houses?
                #  -> event triggern, welches dann die eigentliche veränderung übernimmt?
                #  -> einfacher: eine setter-klasse, die im default einfach nur den wert setzt und mit
                #     if/else sonderfälle behandelt
                setattr(target_instance, effect.attribute, new_value)
