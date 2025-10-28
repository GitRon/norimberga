import pytest

from apps.city.tests.factories import BuildingFactory, TileFactory
from apps.edict.services.edict_activation import EdictActivationService
from apps.edict.tests.factories import EdictFactory
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_edict_activation_with_sufficient_prestige():
    """Test that edict can be activated when prestige requirement is met."""
    savegame = SavegameFactory.create(coins=1000)
    building = BuildingFactory.create(level=2, prestige=15)
    TileFactory.create(savegame=savegame, building=building)

    edict = EdictFactory.create(cost_coins=100, required_prestige=10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_edict_activation_with_insufficient_prestige():
    """Test that edict cannot be activated when prestige requirement is not met."""
    savegame = SavegameFactory.create(coins=1000)
    building = BuildingFactory.create(level=2, prestige=5)
    TileFactory.create(savegame=savegame, building=building)

    edict = EdictFactory.create(cost_coins=100, required_prestige=10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is False
    assert "prestige" in result.message.lower()
    assert "10" in result.message


@pytest.mark.django_db
def test_edict_activation_with_no_prestige_requirement():
    """Test that edict can be activated when there is no prestige requirement."""
    savegame = SavegameFactory.create(coins=1000)

    edict = EdictFactory.create(cost_coins=100, required_prestige=None)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_edict_activation_with_exact_prestige():
    """Test that edict can be activated when prestige exactly matches requirement."""
    savegame = SavegameFactory.create(coins=1000)
    building = BuildingFactory.create(level=2, prestige=10)
    TileFactory.create(savegame=savegame, building=building)

    edict = EdictFactory.create(cost_coins=100, required_prestige=10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True


@pytest.mark.django_db
def test_edict_activation_prestige_check_before_cost_validation():
    """Test that prestige requirement is checked before cost validation."""
    savegame = SavegameFactory.create(coins=50)  # Not enough coins
    building = BuildingFactory.create(level=2, prestige=5)  # Not enough prestige
    TileFactory.create(savegame=savegame, building=building)

    edict = EdictFactory.create(cost_coins=100, required_prestige=10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    # Should fail on prestige requirement first
    assert result.success is False
    assert "prestige" in result.message.lower()


@pytest.mark.django_db
def test_edict_activation_with_multiple_buildings():
    """Test that prestige is correctly calculated from multiple buildings."""
    savegame = SavegameFactory.create(coins=1000)
    building1 = BuildingFactory.create(level=2, prestige=3)
    building2 = BuildingFactory.create(level=3, prestige=5)
    building3 = BuildingFactory.create(level=2, prestige=2)
    TileFactory.create(savegame=savegame, building=building1)
    TileFactory.create(savegame=savegame, building=building2)
    TileFactory.create(savegame=savegame, building=building3)

    edict = EdictFactory.create(cost_coins=100, required_prestige=10)
    service = EdictActivationService(savegame=savegame, edict=edict)

    result = service.process()

    assert result.success is True
