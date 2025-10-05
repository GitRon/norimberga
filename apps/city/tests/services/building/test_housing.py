import pytest

from apps.city.services.building.housing import BuildingHousingService
from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory, SavegameFactory, TileFactory


@pytest.mark.django_db
def test_building_housing_service_init():
    """Test BuildingHousingService initialization."""
    # Create a savegame to pass to the service
    savegame = SavegameFactory()

    service = BuildingHousingService(savegame=savegame)

    assert service.savegame == savegame


@pytest.mark.django_db
def test_building_housing_service_init_creates_savegame():
    """Test BuildingHousingService accepts a savegame parameter."""
    # Create a savegame to pass to the service
    savegame = SavegameFactory()

    service = BuildingHousingService(savegame=savegame)

    assert service.savegame is not None
    assert service.savegame == savegame


@pytest.mark.django_db
def test_building_housing_service_calculate_max_space_with_buildings():
    """Test calculate_max_space returns sum of housing space from buildings."""
    savegame = SavegameFactory()

    # Create buildings with different housing spaces
    building_type = BuildingTypeFactory()
    building1 = BuildingFactory(building_type=building_type, housing_space=5)
    building2 = BuildingFactory(building_type=building_type, housing_space=3)
    building3 = BuildingFactory(building_type=building_type, housing_space=2)

    # Create tiles with these buildings
    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=building3)

    service = BuildingHousingService(savegame=savegame)
    result = service.calculate_max_space()

    assert result == 10  # 5 + 3 + 2


@pytest.mark.django_db
def test_building_housing_service_calculate_max_space_no_buildings():
    """Test calculate_max_space returns 0 when no buildings have housing space."""
    savegame = SavegameFactory()

    # Create tile without building
    TileFactory(savegame=savegame, building=None)

    service = BuildingHousingService(savegame=savegame)
    result = service.calculate_max_space()

    assert result == 0
