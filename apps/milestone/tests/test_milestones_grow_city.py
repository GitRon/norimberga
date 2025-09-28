import pytest

from apps.city.tests.factories import SavegameFactory
from apps.milestone.conditions.population import MinPopulationCondition
from apps.milestone.milestones.grow_city import GrowCityMilestone


@pytest.mark.django_db
def test_grow_city_milestone_init():
    """Test GrowCityMilestone initialization."""
    savegame = SavegameFactory()
    milestone = GrowCityMilestone(savegame_id=savegame.id)

    assert milestone.savegame == savegame


@pytest.mark.django_db
def test_grow_city_milestone_has_population_condition():
    """Test GrowCityMilestone has the correct population condition."""
    savegame = SavegameFactory()
    milestone = GrowCityMilestone(savegame_id=savegame.id)

    assert len(milestone.conditions) == 1
    condition = milestone.conditions[0]
    assert isinstance(condition, MinPopulationCondition)
    assert condition.min_population == 15


@pytest.mark.django_db
def test_grow_city_milestone_is_accomplished_with_sufficient_population():
    """Test milestone is accomplished when population >= 15."""
    savegame = SavegameFactory(population=20)
    milestone = GrowCityMilestone(savegame_id=savegame.id)

    assert milestone.is_accomplished() is True


@pytest.mark.django_db
def test_grow_city_milestone_is_accomplished_with_exact_population():
    """Test milestone is accomplished when population == 15."""
    savegame = SavegameFactory(population=15)
    milestone = GrowCityMilestone(savegame_id=savegame.id)

    assert milestone.is_accomplished() is True


@pytest.mark.django_db
def test_grow_city_milestone_is_not_accomplished_with_insufficient_population():
    """Test milestone is not accomplished when population < 15."""
    savegame = SavegameFactory(population=10)
    milestone = GrowCityMilestone(savegame_id=savegame.id)

    assert milestone.is_accomplished() is False


@pytest.mark.django_db
def test_grow_city_milestone_is_not_accomplished_with_zero_population():
    """Test milestone is not accomplished when population is 0."""
    savegame = SavegameFactory(population=0)
    milestone = GrowCityMilestone(savegame_id=savegame.id)

    assert milestone.is_accomplished() is False
