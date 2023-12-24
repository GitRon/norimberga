from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError

from apps.city.models import Building, Tile


class TileBuildingForm(forms.ModelForm):
    class Meta:
        model = Tile
        fields = ("building",)

    def __init__(self, savegame, *args, **kwargs):
        self.savegame = savegame

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False

        super().__init__(*args, **kwargs)

        building_qs = Building.objects.filter(allowed_terrains=self.instance.terrain)
        if self.instance.building:
            building_qs = building_qs.exclude(id=self.instance.building.id)
        self.fields["building"].queryset = building_qs

    def clean_building(self):
        building = self.cleaned_data["building"]

        if building and building.building_costs > self.savegame.coins:
            raise ValidationError("You don't have enough coin.")

        return building
