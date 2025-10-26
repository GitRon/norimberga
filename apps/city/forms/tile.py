from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError

from apps.city.fields.building import BuildingModelChoiceField
from apps.city.models import Building, Tile


class TileBuildingForm(forms.ModelForm):
    tile = forms.ModelChoiceField(
        queryset=Tile.objects.all(), disabled=True, required=False, widget=forms.HiddenInput()
    )
    current_building = forms.ModelChoiceField(queryset=Building.objects.all(), disabled=True, required=False)
    building = BuildingModelChoiceField(queryset=Building.objects.none(), required=False, empty_label=None)

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

        # If we already have a building, only allow upgrading to the next level
        if self.instance.building:
            buildings = Building.objects.filter(
                building_type=self.instance.building.building_type, level=self.instance.building.level + 1
            )
        else:
            # Get all non-unique buildings allowed by this tile terrain, having level one
            unique_buildings = Building.objects.filter(
                tiles__savegame=self.instance.savegame, building_type__is_unique=True
            )
            buildings = Building.objects.filter(building_type__allowed_terrains=self.instance.terrain, level=1).exclude(
                id__in=unique_buildings
            )

            # If this tile is not adjacent to a city-tile, we can't build city-buildings
            if not self.instance.is_adjacent_to_city_building():
                buildings = buildings.exclude(building_type__is_city=True, building_type__is_country=False)

        self.fields["building"].queryset = buildings.distinct()

    def clean_building(self) -> Building | None:
        building = self.cleaned_data["building"]

        if building and building.building_costs > self.savegame.coins:
            raise ValidationError("You don't have enough coin.")

        # Check demolition costs when demolishing
        if (
            self.instance.building
            and building is None
            and self.instance.building.demolition_costs > self.savegame.coins
        ):
            raise ValidationError("You don't have enough coins to demolish this building.")

        # Allow upgrading unique buildings and demolishing ruins, but prevent demolishing other unique buildings
        if (
            self.instance.building
            and self.instance.building.building_type.is_unique
            and self.instance.building.building_type.type != self.instance.building.building_type.Type.RUINS
            and (building is None or building.building_type != self.instance.building.building_type)
        ):
            raise ValidationError("You can't demolish a unique building.")

        # Prevent building on edge tiles
        if building and self.instance.is_edge_tile():
            raise ValidationError("You can't build on edge tiles.")

        return building
