from unittest import mock

import pytest

from apps.city.events.effects.savegame.increase_population_absolute import IncreasePopulationAbsolute
from apps.city.models import Savegame
from apps.city.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_increase_population_absolute_init():
    """Test IncreasePopulationAbsolute initialization with parameters."""
    effect = IncreasePopulationAbsolute(new_population=40)

    assert effect.new_population == 40


@pytest.mark.django_db
def test_increase_population_absolute_process_normal_increase():
    """Test process increases population by specified amount."""
    savegame = SavegameFactory(population=60)
    effect = IncreasePopulationAbsolute(new_population=25)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_absolute.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 200

        effect.process(savegame)

        savegame.refresh_from_db()
        assert savegame.population == 85


@pytest.mark.django_db
def test_increase_population_absolute_process_housing_limit():
    """Test process respects maximum housing capacity."""
    savegame = SavegameFactory(population=80)
    effect = IncreasePopulationAbsolute(new_population=50)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_absolute.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 100  # Housing limit

        effect.process(savegame)

        savegame.refresh_from_db()
        assert savegame.population == 100  # Limited by housing capacity


@pytest.mark.django_db
def test_increase_population_absolute_process_exact_housing_limit():
    """Test process handles exact housing capacity correctly."""
    savegame = SavegameFactory(population=75)
    effect = IncreasePopulationAbsolute(new_population=25)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_absolute.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 100

        effect.process(savegame)

        savegame.refresh_from_db()
        assert savegame.population == 100


@pytest.mark.django_db
def test_increase_population_absolute_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(population=0)
    effect = IncreasePopulationAbsolute(new_population=30)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_absolute.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 150

        effect.process(savegame)

        savegame.refresh_from_db()
        expected_population = min(0 + 30, 150)  # Default population (0) + new_population, max housing
        assert savegame.population == expected_population


@pytest.mark.django_db
def test_increase_population_absolute_process_zero_increase():
    """Test process with zero increase amount."""
    savegame = SavegameFactory(population=90)
    effect = IncreasePopulationAbsolute(new_population=0)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_absolute.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 200

        effect.process(savegame)

        savegame.refresh_from_db()
        assert savegame.population == 90


@pytest.mark.django_db
def test_increase_population_absolute_process_calls_housing_service():
    """Test process calls BuildingHousingService to calculate max space."""
    savegame = SavegameFactory(population=40)
    effect = IncreasePopulationAbsolute(new_population=20)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_absolute.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 150

        effect.process(savegame)

        mock_service.assert_called_once()
        mock_service.return_value.calculate_max_space.assert_called_once()
