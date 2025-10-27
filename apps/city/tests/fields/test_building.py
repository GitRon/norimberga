import pytest

from apps.city.fields.building import BuildingModelChoiceField
from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory


@pytest.mark.django_db
def test_building_model_choice_field_label_from_instance():
    """Test BuildingModelChoiceField formats label correctly."""
    building_type = BuildingTypeFactory.create()
    building = BuildingFactory(name="Manor House", building_type=building_type, building_costs=150)

    field = BuildingModelChoiceField(queryset=None)
    label = field.label_from_instance(building)

    assert label == "Manor House (150 coins)"


@pytest.mark.django_db
def test_building_model_choice_field_label_zero_cost():
    """Test BuildingModelChoiceField formats label with zero cost."""
    building_type = BuildingTypeFactory.create()
    building = BuildingFactory(name="Free Building", building_type=building_type, building_costs=0)

    field = BuildingModelChoiceField(queryset=None)
    label = field.label_from_instance(building)

    assert label == "Free Building (0 coins)"


def test_building_model_choice_field_inheritance():
    """Test BuildingModelChoiceField inherits from ModelChoiceField."""
    from django.forms import ModelChoiceField

    field = BuildingModelChoiceField(queryset=None)
    assert isinstance(field, ModelChoiceField)
