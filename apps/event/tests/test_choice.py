import pytest

from apps.city.events.effects.savegame.decrease_coins import DecreaseCoins
from apps.city.events.effects.savegame.increase_coins import IncreaseCoins
from apps.event.events.choice import Choice
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_choice_apply_effects_applies_single_effect():
    """Test that apply_effects applies a single effect to the savegame."""
    # Arrange
    savegame = SavegameFactory(coins=100)
    effect = IncreaseCoins(coins=50)
    choice = Choice(
        label="Test Choice",
        description="Test Description",
        effects=[effect],
    )

    # Act
    choice.apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins == 150


@pytest.mark.django_db
def test_choice_apply_effects_applies_multiple_effects():
    """Test that apply_effects applies multiple effects to the savegame."""
    # Arrange
    savegame = SavegameFactory(coins=100)
    effects = [
        IncreaseCoins(coins=50),
        DecreaseCoins(coins=20),
    ]
    choice = Choice(
        label="Test Choice",
        description="Test Description",
        effects=effects,
    )

    # Act
    choice.apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins == 130


@pytest.mark.django_db
def test_choice_apply_effects_handles_none_effects():
    """Test that apply_effects ignores None effects."""
    # Arrange
    savegame = SavegameFactory(coins=100)
    effects = [
        IncreaseCoins(coins=50),
        None,  # This should be ignored
        DecreaseCoins(coins=20),
    ]
    choice = Choice(
        label="Test Choice",
        description="Test Description",
        effects=effects,
    )

    # Act
    choice.apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins == 130


@pytest.mark.django_db
def test_choice_apply_effects_with_empty_effects_list():
    """Test that apply_effects handles empty effects list gracefully."""
    # Arrange
    savegame = SavegameFactory(coins=100)
    choice = Choice(
        label="Test Choice",
        description="Test Description",
        effects=[],
    )

    # Act
    choice.apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins == 100  # No change
