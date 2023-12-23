from crispy_forms.helper import FormHelper
from django import forms

from apps.city.models import Tile


class TileBuildingForm(forms.ModelForm):
    class Meta:
        model = Tile
        fields = ("building",)

    def __init__(self, *args, **kwargs):
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False

        super().__init__(*args, **kwargs)
