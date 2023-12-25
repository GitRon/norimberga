from django.forms import ModelChoiceField


class BuildingModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.building_costs} coins)"
