from unittest import mock

import pytest

from apps.city.events.effects.savegame.increase_population_relative import IncreasePopulationRelative
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_increase_population_relative_init():
    """Test IncreasePopulationRelative initialization with parameters."""
    effect = IncreasePopulationRelative(new_population_percentage=0.15)

    assert effect.new_population == 0.15


@pytest.mark.django_db
def test_increase_population_relative_process_percentage_increase():
    """Test process increases population by specified percentage."""
    savegame = SavegameFactory(population=100)
    effect = IncreasePopulationRelative(new_population_percentage=0.2)  # 20% increase

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 300

        effect.process(savegame=savegame)

        savegame.refresh_from_db()
        assert savegame.population == 120  # 100 * (1 + 0.2) = 120


@pytest.mark.django_db
def test_increase_population_relative_process_rounding():
    """Test process handles rounding correctly."""
    savegame = SavegameFactory(population=77)
    effect = IncreasePopulationRelative(new_population_percentage=0.1)  # 10% increase

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 200

        effect.process(savegame=savegame)

        savegame.refresh_from_db()
        assert savegame.population == 85  # round(77 * 1.1) = round(84.7) = 85


@pytest.mark.django_db
def test_increase_population_relative_process_housing_limit():
    """Test process respects maximum housing capacity."""
    savegame = SavegameFactory(population=90)
    effect = IncreasePopulationRelative(new_population_percentage=0.5)  # 50% increase

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 100  # Housing limit

        effect.process(savegame=savegame)

        savegame.refresh_from_db()
        assert savegame.population == 100  # Limited by housing capacity


@pytest.mark.django_db
def test_increase_population_relative_process_exact_housing_limit():
    """Test process handles exact housing capacity correctly."""
    savegame = SavegameFactory(population=80)
    effect = IncreasePopulationRelative(new_population_percentage=0.25)  # 25% increase

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 100

        effect.process(savegame=savegame)

        savegame.refresh_from_db()
        assert savegame.population == 100  # 80 * 1.25 = 100, exactly at limit


@pytest.mark.django_db
def test_increase_population_relative_process_creates_savegame():
    """Test process works with newly created savegame."""
    savegame = SavegameFactory(population=0)
    effect = IncreasePopulationRelative(new_population_percentage=0.3)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 200

        effect.process(savegame=savegame)

        savegame.refresh_from_db()
        expected_population = min(round(0 * (1 + 0.3)), 200)  # Default population (0) * (1 + percentage)
        assert savegame.population == expected_population


@pytest.mark.django_db
def test_increase_population_relative_process_zero_percentage():
    """Test process with zero percentage increase."""
    savegame = SavegameFactory(population=110)
    effect = IncreasePopulationRelative(new_population_percentage=0.0)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 300

        effect.process(savegame=savegame)

        savegame.refresh_from_db()
        assert savegame.population == 110


@pytest.mark.django_db
def test_increase_population_relative_process_calls_housing_service():
    """Test process calls BuildingHousingService to calculate max space."""
    savegame = SavegameFactory(population=60)
    effect = IncreasePopulationRelative(new_population_percentage=0.1)

    with mock.patch(
        "apps.city.events.effects.savegame.increase_population_relative.BuildingHousingService"
    ) as mock_service:
        mock_service.return_value.calculate_max_space.return_value = 150

        effect.process(savegame=savegame)

        mock_service.assert_called_once()
        mock_service.return_value.calculate_max_space.assert_called_once()
