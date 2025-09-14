import pytest

from apps.city.services.building.housing import BuildingHousingService
from apps.city.tests.factories import BuildingFactory, BuildingTypeFactory, SavegameFactory, TileFactory


@pytest.mark.django_db
def test_building_housing_service_init():
    """Test BuildingHousingService initialization."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    # Create a savegame with id=1 to test get_or_create
    existing_savegame = SavegameFactory(id=1)

    service = BuildingHousingService()

    assert service.savegame == existing_savegame
    assert service.savegame.id == 1


@pytest.mark.django_db
def test_building_housing_service_init_creates_savegame():
    """Test BuildingHousingService creates savegame if doesn't exist."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    service = BuildingHousingService()

    assert service.savegame is not None
    assert service.savegame.id == 1


@pytest.mark.django_db
def test_building_housing_service_calculate_max_space_with_buildings():
    """Test calculate_max_space returns sum of housing space from buildings."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create buildings with different housing spaces
    building_type = BuildingTypeFactory()
    building1 = BuildingFactory(building_type=building_type, housing_space=5)
    building2 = BuildingFactory(building_type=building_type, housing_space=3)
    building3 = BuildingFactory(building_type=building_type, housing_space=2)

    # Create tiles with these buildings
    TileFactory(savegame=savegame, building=building1)
    TileFactory(savegame=savegame, building=building2)
    TileFactory(savegame=savegame, building=building3)

    service = BuildingHousingService()
    result = service.calculate_max_space()

    assert result == 10  # 5 + 3 + 2


@pytest.mark.django_db
def test_building_housing_service_calculate_max_space_no_buildings():
    """Test calculate_max_space returns None when no buildings have housing space."""
    # Clear any existing savegame with id=1
    from apps.city.models import Savegame

    Savegame.objects.filter(id=1).delete()

    savegame = SavegameFactory(id=1)

    # Create tile without building
    TileFactory(savegame=savegame, building=None)

    service = BuildingHousingService()
    result = service.calculate_max_space()

    assert result is None
