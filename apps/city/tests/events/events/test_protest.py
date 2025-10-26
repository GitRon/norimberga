from unittest import mock

import pytest

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.decrease_population_absolute import DecreasePopulationAbsolute
from apps.city.events.events.protest import Event as ProtestEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_protest_event_init():
    """Test ProtestEvent initialization and class attributes."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [3, 20]  # lost_population, lost_coins

        event = ProtestEvent(savegame=savegame)

        assert event.PROBABILITY == 60
        assert event.TITLE == "Protest"
        assert event.savegame.id == savegame.id
        assert event.initial_population == 100
        assert event.initial_coins == 100
        assert event.lost_population == 3
        assert event.lost_coins == 20


@pytest.mark.django_db
def test_protest_event_init_accepts_savegame():
    """Test ProtestEvent accepts a savegame parameter."""
    savegame = SavegameFactory(unrest=40, coins=50)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [2, 15]

        event = ProtestEvent(savegame=savegame)

        assert event.savegame.id == savegame.id


@pytest.mark.django_db
def test_protest_event_random_values():
    """Test lost_population and lost_coins use random values."""
    savegame = SavegameFactory(population=200, unrest=50, coins=200)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [5, 30]

        event = ProtestEvent(savegame=savegame)

        assert event.lost_population == 5
        assert event.lost_coins == 30


@pytest.mark.django_db
def test_protest_event_get_probability_unrest_below_threshold():
    """Test get_probability returns 0 when unrest is below 25."""
    savegame = SavegameFactory(population=100, unrest=24, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_protest_event_get_probability_unrest_at_lower_threshold():
    """Test get_probability when unrest is exactly 25."""
    savegame = SavegameFactory(population=100, unrest=25, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        # At unrest 25, probability should be 0 (minimum of range)
        assert probability == 0


@pytest.mark.django_db
def test_protest_event_get_probability_unrest_in_range():
    """Test get_probability when unrest is in valid range."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        # At unrest 50, halfway between 25 and 75
        # unrest_factor = (50 - 25) / 50 = 0.5
        # probability = 60 * 0.5 = 30
        assert probability == 30


@pytest.mark.django_db
def test_protest_event_get_probability_unrest_at_upper_threshold():
    """Test get_probability returns 0 when unrest is exactly 75."""
    savegame = SavegameFactory(population=100, unrest=75, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_protest_event_get_probability_unrest_above_threshold():
    """Test get_probability returns 0 when unrest is above 75."""
    savegame = SavegameFactory(population=100, unrest=80, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_protest_event_get_probability_zero_unrest():
    """Test get_probability returns 0 when unrest is zero."""
    savegame = SavegameFactory(population=100, unrest=0, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_protest_event_get_probability_zero_population():
    """Test get_probability returns 0 when population is zero."""
    savegame = SavegameFactory(population=0, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)
        probability = event.get_probability()

        assert probability == 0


@pytest.mark.django_db
def test_protest_event_prepare_effect_decrease_population():
    """Test _prepare_effect_decrease_population returns correct effect."""
    savegame = SavegameFactory(population=150, unrest=40, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [4, 25]

        event = ProtestEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_population()

        assert isinstance(effect, DecreasePopulationAbsolute)
        assert effect.lost_population == 4


@pytest.mark.django_db
def test_protest_event_prepare_effect_decrease_coins():
    """Test _prepare_effect_decrease_coins returns correct effect."""
    savegame = SavegameFactory(population=150, unrest=40, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [3, 18]

        event = ProtestEvent(savegame=savegame)
        effect = event._prepare_effect_decrease_coins()

        assert isinstance(effect, DecreaseCoins)
        assert effect.coins == 18


@pytest.mark.django_db
def test_protest_event_get_verbose_text():
    """Test get_verbose_text returns correct description."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [3, 20]

        event = ProtestEvent(savegame=savegame)
        initial_population = event.initial_population
        initial_coins = event.initial_coins

        # Simulate effect processing (decrease population and coins)
        lost_population = event.lost_population
        lost_coins = event.lost_coins
        savegame.population = savegame.population - lost_population
        savegame.coins = savegame.coins - lost_coins
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "Citizens gathered in the streets to protest against the city council. "
            f"The protest turned violent, resulting in {initial_population - savegame.population} casualties "
            f"and {initial_coins - savegame.coins} coins looted by the protesters."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_protest_event_get_verbose_text_no_coins_lost():
    """Test get_verbose_text when no coins are actually lost."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [2, 15]

        event = ProtestEvent(savegame=savegame)
        initial_population = event.initial_population

        # Simulate only population loss, no coin loss
        savegame.population = savegame.population - event.lost_population
        savegame.save()

        verbose_text = event.get_verbose_text()

        expected_text = (
            "Citizens gathered in the streets to protest against the city council. "
            f"The protest turned violent, resulting in {initial_population - savegame.population} casualties."
        )
        assert verbose_text == expected_text


@pytest.mark.django_db
def test_protest_event_random_range():
    """Test that random.randint is called with correct ranges."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [3, 20]

        ProtestEvent(savegame=savegame)

        assert mock_randint.call_count == 2
        mock_randint.assert_any_call(1, 5)
        mock_randint.assert_any_call(10, 30)


@pytest.mark.django_db
def test_protest_event_minimum_values():
    """Test event with minimum random values."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [1, 10]

        event = ProtestEvent(savegame=savegame)

        assert event.lost_population == 1
        assert event.lost_coins == 10


@pytest.mark.django_db
def test_protest_event_maximum_values():
    """Test event with maximum random values."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [5, 30]

        event = ProtestEvent(savegame=savegame)

        assert event.lost_population == 5
        assert event.lost_coins == 30


@pytest.mark.django_db
def test_protest_event_unrest_boundary_24():
    """Test event does not trigger at unrest 24."""
    savegame = SavegameFactory(population=100, unrest=24, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)

        assert event.get_probability() == 0


@pytest.mark.django_db
def test_protest_event_unrest_boundary_74():
    """Test event triggers at unrest 74."""
    savegame = SavegameFactory(population=100, unrest=74, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint"):
        event = ProtestEvent(savegame=savegame)

        # At unrest 74, near maximum of range
        # unrest_factor = (74 - 25) / 50 = 0.98
        # probability = 60 * 0.98 = 58.8
        assert event.get_probability() == 58.8


@pytest.mark.django_db
def test_protest_event_probability_scales_with_unrest():
    """Test that probability increases as unrest increases within valid range."""
    with mock.patch("apps.city.events.events.protest.random.randint"):
        # Test at unrest 30
        savegame_30 = SavegameFactory(population=100, unrest=30, coins=100)
        event_30 = ProtestEvent(savegame=savegame_30)
        prob_30 = event_30.get_probability()

        # Test at unrest 60
        savegame_60 = SavegameFactory(population=100, unrest=60, coins=100)
        event_60 = ProtestEvent(savegame=savegame_60)
        prob_60 = event_60.get_probability()

        # Probability should increase with unrest
        assert prob_60 > prob_30
        # unrest_factor at 30 = (30 - 25) / 50 = 0.1, prob = 60 * 0.1 = 6
        assert prob_30 == 6
        # unrest_factor at 60 = (60 - 25) / 50 = 0.7, prob = 60 * 0.7 = 42
        assert prob_60 == 42


@pytest.mark.django_db
def test_protest_event_process():
    """Test process method executes all effects and returns verbose text."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [3, 20]

        event = ProtestEvent(savegame=savegame)
        result = event.process()

        # Verify population and coins decreased
        savegame.refresh_from_db()
        assert savegame.population == 97
        assert savegame.coins == 80

        # Verify verbose text is returned
        assert "Citizens gathered in the streets to protest against the city council" in result
        assert "3 casualties" in result
        assert "20 coins looted by the protesters" in result


@pytest.mark.django_db
def test_protest_event_get_effects():
    """Test get_effects returns both decrease population and decrease coins effects."""
    savegame = SavegameFactory(population=100, unrest=50, coins=100)

    with mock.patch("apps.city.events.events.protest.random.randint") as mock_randint:
        mock_randint.side_effect = [4, 25]

        event = ProtestEvent(savegame=savegame)
        effects = event.get_effects()

        assert len(effects) == 2

        # Find effects by type (order may vary)
        population_effect = next((e for e in effects if isinstance(e, DecreasePopulationAbsolute)), None)
        coins_effect = next((e for e in effects if isinstance(e, DecreaseCoins)), None)

        assert population_effect is not None
        assert coins_effect is not None
        assert population_effect.lost_population == 4
        assert coins_effect.coins == 25
