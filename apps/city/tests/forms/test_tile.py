from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from apps.city.forms.tile import TileBuildingForm
from apps.city.tests.factories import (
    BuildingFactory,
    BuildingTypeFactory,
    SavegameFactory,
    TerrainFactory,
    TileFactory,
    UniqueBuildingTypeFactory,
)


@pytest.mark.django_db
def test_tile_building_form_initialization():
    """Test TileBuildingForm initializes correctly."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()
    tile = TileFactory(savegame=savegame, terrain=terrain)

    form = TileBuildingForm(savegame=savegame, instance=tile)

    assert form.savegame == savegame
    assert form.instance == tile
    assert form.fields["tile"].initial == tile
    assert form.fields["current_building"].initial == tile.building


@pytest.mark.django_db
def test_tile_building_form_building_queryset_basic():
    """Test form includes allowed buildings for terrain."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create building type allowed on this terrain (explicitly non-unique)
    building_type = BuildingTypeFactory(is_unique=False)
    building_type.allowed_terrains.add(terrain)
    allowed_building = BuildingFactory(building_type=building_type, level=1)

    # Create building type not allowed on this terrain
    other_terrain = TerrainFactory()
    other_building_type = BuildingTypeFactory(is_unique=False)
    other_building_type.allowed_terrains.add(other_terrain)
    not_allowed_building = BuildingFactory(building_type=other_building_type, level=1)

    tile = TileFactory(savegame=savegame, terrain=terrain, building=None)

    # Mock the tile method to avoid adjacency check complexity
    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=True):
        form = TileBuildingForm(savegame=savegame, instance=tile)

        building_queryset = form.fields["building"].queryset
        building_ids = list(building_queryset.values_list("id", flat=True))

        assert allowed_building.id in building_ids
        assert not_allowed_building.id not in building_ids


@pytest.mark.django_db
def test_tile_building_form_excludes_unique_buildings():
    """Test form excludes unique buildings already built in savegame."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create unique building type
    unique_building_type = UniqueBuildingTypeFactory()
    unique_building_type.allowed_terrains.add(terrain)
    unique_building = BuildingFactory(building_type=unique_building_type, level=1)

    # Place unique building on another tile in same savegame
    other_tile = TileFactory(savegame=savegame, x=0, y=0, building=unique_building)

    # Create new tile to test
    tile = TileFactory(savegame=savegame, terrain=terrain, x=1, y=0, building=None)

    form = TileBuildingForm(savegame=savegame, instance=tile)

    building_queryset = form.fields["building"].queryset
    building_ids = list(building_queryset.values_list("id", flat=True))

    # Unique building should be excluded since it's already built
    assert unique_building.id not in building_ids


@pytest.mark.django_db
def test_tile_building_form_excludes_city_buildings_without_adjacent_city():
    """Test form excludes city-only buildings when not adjacent to city building."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create city-only building type (explicitly non-unique)
    city_building_type = BuildingTypeFactory(is_city=True, is_country=False, is_unique=False)
    city_building_type.allowed_terrains.add(terrain)
    city_building = BuildingFactory(building_type=city_building_type, level=1)

    # Create tile with no adjacent city buildings
    tile = TileFactory(savegame=savegame, terrain=terrain, building=None)

    # Mock is_adjacent_to_city_building to return False
    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=False):
        form = TileBuildingForm(savegame=savegame, instance=tile)

        building_queryset = form.fields["building"].queryset
        building_ids = list(building_queryset.values_list("id", flat=True))

        # City-only building should be excluded
        assert city_building.id not in building_ids


@pytest.mark.django_db
def test_tile_building_form_includes_city_buildings_with_adjacent_city():
    """Test form includes city buildings when adjacent to city building."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create city-only building type (explicitly non-unique)
    city_building_type = BuildingTypeFactory(is_city=True, is_country=False, is_unique=False)
    city_building_type.allowed_terrains.add(terrain)
    city_building = BuildingFactory(building_type=city_building_type, level=1)

    # Create tile adjacent to city building
    tile = TileFactory(savegame=savegame, terrain=terrain, building=None)

    # Mock is_adjacent_to_city_building to return True
    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=True):
        form = TileBuildingForm(savegame=savegame, instance=tile)

        building_queryset = form.fields["building"].queryset
        building_ids = list(building_queryset.values_list("id", flat=True))

        # City building should be included
        assert city_building.id in building_ids


@pytest.mark.django_db
def test_tile_building_form_includes_country_buildings_always():
    """Test form includes country buildings regardless of city adjacency."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create country-only building type (explicitly non-unique)
    country_building_type = BuildingTypeFactory(is_city=False, is_country=True, is_unique=False)
    country_building_type.allowed_terrains.add(terrain)
    country_building = BuildingFactory(building_type=country_building_type, level=1)

    tile = TileFactory(savegame=savegame, terrain=terrain, building=None)

    # Mock is_adjacent_to_city_building to return False
    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=False):
        form = TileBuildingForm(savegame=savegame, instance=tile)

        building_queryset = form.fields["building"].queryset
        building_ids = list(building_queryset.values_list("id", flat=True))

        # Country building should still be included
        assert country_building.id in building_ids


@pytest.mark.django_db
def test_tile_building_form_includes_both_buildings():
    """Test form includes both city+country buildings regardless of adjacency."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create both city and country building type (explicitly non-unique)
    both_building_type = BuildingTypeFactory(is_city=True, is_country=True, is_unique=False)
    both_building_type.allowed_terrains.add(terrain)
    both_building = BuildingFactory(building_type=both_building_type, level=1)

    tile = TileFactory(savegame=savegame, terrain=terrain, building=None)

    # Mock is_adjacent_to_city_building to return False
    with mock.patch.object(tile, "is_adjacent_to_city_building", return_value=False):
        form = TileBuildingForm(savegame=savegame, instance=tile)

        building_queryset = form.fields["building"].queryset
        building_ids = list(building_queryset.values_list("id", flat=True))

        # Both building should be included (has is_country=True)
        assert both_building.id in building_ids


@pytest.mark.django_db
def test_tile_building_form_upgrade_existing_building():
    """Test form allows upgrading existing building."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create building type with level 1 and 2 buildings
    building_type = BuildingTypeFactory()
    building_type.allowed_terrains.add(terrain)
    level1_building = BuildingFactory(building_type=building_type, level=1)
    level2_building = BuildingFactory(building_type=building_type, level=2)

    # Create tile with level 1 building
    tile = TileFactory(savegame=savegame, terrain=terrain, building=level1_building)

    form = TileBuildingForm(savegame=savegame, instance=tile)

    building_queryset = form.fields["building"].queryset
    building_ids = list(building_queryset.values_list("id", flat=True))

    # Should exclude current building but include upgrade
    assert level1_building.id not in building_ids
    assert level2_building.id in building_ids


@pytest.mark.django_db
def test_tile_building_form_clean_building_insufficient_coins():
    """Test form validation fails when insufficient coins."""
    savegame = SavegameFactory(coins=10)
    terrain = TerrainFactory()
    tile = TileFactory(savegame=savegame, terrain=terrain)

    # Create expensive building
    building_type = BuildingTypeFactory()
    building_type.allowed_terrains.add(terrain)
    expensive_building = BuildingFactory(building_type=building_type, building_costs=100, level=1)

    form = TileBuildingForm(savegame=savegame, instance=tile)
    form.cleaned_data = {"building": expensive_building}

    with pytest.raises(ValidationError) as exc_info:
        form.clean_building()

    assert "You don't have enough coin." in str(exc_info.value)


@pytest.mark.django_db
def test_tile_building_form_clean_building_sufficient_coins():
    """Test form validation passes when sufficient coins."""
    savegame = SavegameFactory(coins=100)
    terrain = TerrainFactory()
    tile = TileFactory(savegame=savegame, terrain=terrain)

    # Create affordable building
    building_type = BuildingTypeFactory()
    building_type.allowed_terrains.add(terrain)
    affordable_building = BuildingFactory(building_type=building_type, building_costs=50, level=1)

    form = TileBuildingForm(savegame=savegame, instance=tile)
    form.cleaned_data = {"building": affordable_building}

    result = form.clean_building()
    assert result == affordable_building


@pytest.mark.django_db
def test_tile_building_form_clean_building_demolish_unique():
    """Test form validation fails when trying to demolish unique building."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create unique building
    unique_building_type = UniqueBuildingTypeFactory()
    unique_building = BuildingFactory(building_type=unique_building_type)

    tile = TileFactory(savegame=savegame, terrain=terrain, building=unique_building)

    form = TileBuildingForm(savegame=savegame, instance=tile)
    form.cleaned_data = {"building": None}  # Trying to demolish (set to None)

    with pytest.raises(ValidationError) as exc_info:
        form.clean_building()

    assert "You can't demolish a unique building." in str(exc_info.value)


@pytest.mark.django_db
def test_tile_building_form_clean_building_demolish_non_unique():
    """Test form validation passes when demolishing non-unique building."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create regular building
    building_type = BuildingTypeFactory(is_unique=False)
    building = BuildingFactory(building_type=building_type)

    tile = TileFactory(savegame=savegame, terrain=terrain, building=building)

    form = TileBuildingForm(savegame=savegame, instance=tile)
    form.cleaned_data = {"building": None}  # Trying to demolish

    result = form.clean_building()
    assert result is None


@pytest.mark.django_db
def test_tile_building_form_clean_building_no_building():
    """Test form validation passes when no building selected."""
    savegame = SavegameFactory()
    terrain = TerrainFactory()
    tile = TileFactory(savegame=savegame, terrain=terrain, building=None)

    form = TileBuildingForm(savegame=savegame, instance=tile)
    form.cleaned_data = {"building": None}

    result = form.clean_building()
    assert result is None


@pytest.mark.django_db
def test_tile_building_form_crispy_helper():
    """Test form has crispy helper configured."""
    savegame = SavegameFactory()
    tile = TileFactory(savegame=savegame)

    form = TileBuildingForm(savegame=savegame, instance=tile)

    assert hasattr(form, "helper")
    assert form.helper.form_tag is False
