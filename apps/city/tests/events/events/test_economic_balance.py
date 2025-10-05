from unittest import mock

import pytest
from django.contrib import messages

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.city.events.events.economic_balance import Event as EconomicBalanceEvent
from apps.city.tests.factories import BuildingFactory, SavegameFactory, TerrainFactory, TileFactory


@pytest.mark.django_db
def test_economic_balance_event_init_positive_balance():
    """Test EconomicBalanceEvent initialization with positive balance."""
    savegame = SavegameFactory()
    balance_data = {
        "balance": 150,
        "taxes": 200,
        "maintenance": 50,
    }

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)

        assert event.PROBABILITY == 100
        assert event.LEVEL == messages.INFO
        assert event.TITLE == "Economic Balance"
        assert event.savegame.id == savegame.id
        assert event.balance == 150
        assert event.taxes == 200
        assert event.maintenance == 50


@pytest.mark.django_db
def test_economic_balance_event_init_negative_balance():
    """Test EconomicBalanceEvent initialization with negative balance."""
    savegame = SavegameFactory()
    balance_data = {
        "balance": -75,
        "taxes": 25,
        "maintenance": 100,
    }

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)

        assert event.balance == -75
        assert event.taxes == 25
        assert event.maintenance == 100


@pytest.mark.django_db
def test_economic_balance_event_get_probability_with_positive_balance():
    """Test get_probability returns base probability when balance is positive."""
    savegame = SavegameFactory()
    balance_data = {"balance": 100, "taxes": 150, "maintenance": 50}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 100


@pytest.mark.django_db
def test_economic_balance_event_get_probability_with_negative_balance():
    """Test get_probability returns base probability when balance is negative."""
    savegame = SavegameFactory()
    balance_data = {"balance": -50, "taxes": 50, "maintenance": 100}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 100


@pytest.mark.django_db
def test_economic_balance_event_get_probability_zero_balance():
    """Test get_probability returns 0 when balance is zero."""
    savegame = SavegameFactory()
    balance_data = {"balance": 0, "taxes": 100, "maintenance": 100}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_economic_balance_event_prepare_effect_positive_balance():
    """Test _prepare_effect_adjust_coins returns IncreaseCoins for positive balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": 120, "taxes": 150, "maintenance": 30}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        effect = event._prepare_effect_adjust_coins()

        assert isinstance(effect, IncreaseCoins)
        assert effect.coins == 120


@pytest.mark.django_db
def test_economic_balance_event_prepare_effect_negative_balance():
    """Test _prepare_effect_adjust_coins returns DecreaseCoins for negative balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": -80, "taxes": 20, "maintenance": 100}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        effect = event._prepare_effect_adjust_coins()

        assert isinstance(effect, DecreaseCoins)
        assert effect.coins == 80


@pytest.mark.django_db
def test_economic_balance_event_prepare_effect_zero_balance():
    """Test _prepare_effect_adjust_coins returns None for zero balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": 0, "taxes": 50, "maintenance": 50}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        effect = event._prepare_effect_adjust_coins()

        assert effect is None


@pytest.mark.django_db
def test_economic_balance_event_get_verbose_text_positive():
    """Test get_verbose_text returns correct description for positive balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": 100, "taxes": 150, "maintenance": 50}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        verbose_text = event.get_verbose_text()

        expected_text = (
            "Tax collection brought in 150 coins while building maintenance "
            "cost 50 coins. The city treasury gained 100 coins."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_economic_balance_event_get_verbose_text_negative():
    """Test get_verbose_text returns correct description for negative balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": -60, "taxes": 40, "maintenance": 100}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        verbose_text = event.get_verbose_text()

        expected_text = (
            "Tax collection brought in 40 coins while building maintenance "
            "cost 100 coins. The city treasury lost 60 coins."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_economic_balance_event_process_positive_balance():
    """Test full event processing workflow with positive balance."""
    savegame = SavegameFactory(coins=500)
    balance_data = {"balance": 100, "taxes": 150, "maintenance": 50}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        result_text = event.process()

        # Verify effect was applied
        savegame.refresh_from_db()
        assert savegame.coins == 600  # 500 + 100 = 600

        # Verify result text is returned
        assert "Tax collection brought in 150 coins" in result_text
        assert "The city treasury gained 100 coins" in result_text


@pytest.mark.django_db
def test_economic_balance_event_process_negative_balance():
    """Test full event processing workflow with negative balance."""
    savegame = SavegameFactory(coins=300)
    balance_data = {"balance": -75, "taxes": 25, "maintenance": 100}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        result_text = event.process()

        # Verify effect was applied
        savegame.refresh_from_db()
        assert savegame.coins == 225  # 300 - 75 = 225

        # Verify result text is returned
        assert "Tax collection brought in 25 coins" in result_text
        assert "The city treasury lost 75 coins" in result_text


@pytest.mark.django_db
def test_economic_balance_event_get_effects_positive():
    """Test get_effects returns list with IncreaseCoins effect for positive balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": 50, "taxes": 100, "maintenance": 50}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        effects = event.get_effects()

        assert len(effects) == 1
        assert isinstance(effects[0], IncreaseCoins)
        assert effects[0].coins == 50


@pytest.mark.django_db
def test_economic_balance_event_get_effects_negative():
    """Test get_effects returns list with DecreaseCoins effect for negative balance."""
    savegame = SavegameFactory()
    balance_data = {"balance": -30, "taxes": 20, "maintenance": 50}

    with mock.patch("apps.city.events.events.economic_balance.get_balance_data") as mock_balance:
        mock_balance.return_value = balance_data

        event = EconomicBalanceEvent(savegame=savegame)
        effects = event.get_effects()

        assert len(effects) == 1
        assert isinstance(effects[0], DecreaseCoins)
        assert effects[0].coins == 30


@pytest.mark.django_db
def test_economic_balance_event_integration_with_real_balance():
    """Test event integration with real balance calculation from buildings."""
    # Create savegame with terrain and buildings
    savegame = SavegameFactory()
    terrain = TerrainFactory()

    # Create buildings with different tax and maintenance values
    building1 = BuildingFactory(taxes=50, maintenance_costs=10)
    building2 = BuildingFactory(taxes=30, maintenance_costs=5)
    building3 = BuildingFactory(taxes=0, maintenance_costs=20)

    TileFactory(savegame=savegame, terrain=terrain, building=building1)
    TileFactory(savegame=savegame, terrain=terrain, building=building2)
    TileFactory(savegame=savegame, terrain=terrain, building=building3)

    # Expected: taxes=80 (50+30), maintenance=35 (10+5+20), balance=45
    event = EconomicBalanceEvent(savegame=savegame)

    assert event.taxes == 80
    assert event.maintenance == 35
    assert event.balance == 45
