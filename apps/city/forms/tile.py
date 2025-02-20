from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError

from apps.city.fields.building import BuildingModelChoiceField
from apps.city.models import Building, Tile


class TileBuildingForm(forms.ModelForm):
    tile = forms.ModelChoiceField(queryset=Tile.objects.all(), disabled=True, required=False)
    current_building = forms.ModelChoiceField(queryset=Building.objects.all(), disabled=True, required=False)
    building = BuildingModelChoiceField(queryset=Building.objects.none(), required=False)

    class Meta:
        model = Tile
        fields = (
            "tile",
            "current_building",
            "building",
        )

    def __init__(self, savegame, *args, **kwargs):
        self.savegame = savegame

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False

        super().__init__(*args, **kwargs)

        self.fields["tile"].initial = self.instance
        self.fields["current_building"].initial = self.instance.building

        # Get all non-unique buildings allowed by this tile terrain, having level one
        unique_buildings = Building.objects.filter(
            tiles__savegame=self.instance.savegame, building_type__is_unique=True
        )
        building_qs = Building.objects.filter(building_type__allowed_terrains=self.instance.terrain, level=1).exclude(
            id__in=unique_buildings
        )

        # If this tile is not adjacent to a city-tile, we can't build city-buildings
        if not self.instance.is_adjacent_to_city_building():
            building_qs = building_qs.exclude(building_type__is_city=True, building_type__is_country=False)

        # If we already have a building, we allow level 2 buildings of the same type
        if self.instance.building:
            building_qs = building_qs.exclude(id=self.instance.building.id) | Building.objects.filter(
                building_type=self.instance.building.building_type, level=self.instance.building.level + 1
            )

        self.fields["building"].queryset = building_qs.distinct()

    def clean_building(self):
        building = self.cleaned_data["building"]

        if building and building.building_costs > self.savegame.coins:
            raise ValidationError("You don't have enough coin.")

        if self.instance.building and self.instance.building.building_type.is_unique:
            raise ValidationError("You can't demolish a unique building.")

        return building
