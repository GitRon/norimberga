from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms

from apps.city.models import Savegame


class SavegameCreateForm(forms.ModelForm):
    class Meta:
        model = Savegame
        fields = ("city_name",)
        labels = {"city_name": "City Name"}
        help_texts = {"city_name": "Choose a name for your medieval city"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id_savegame_create_form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("city_name"),
            Div(
                HTML(
                    "<a href=\"{% url 'city:savegame-list' %}\" "
                    'class="px-4 py-2 bg-gray-300 text-gray-700 text-sm font-medium rounded-md '
                    "hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                    'focus:ring-gray-500">Cancel</a>'
                ),
                Submit(
                    "submit",
                    "Create Savegame",
                    css_class="px-6 py-2 bg-green-600 text-white text-sm font-medium rounded-md "
                    "hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 "
                    "focus:ring-green-500",
                ),
                css_class="flex justify-between items-center mt-6",
            ),
        )
