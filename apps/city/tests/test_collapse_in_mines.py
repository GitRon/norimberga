import pytest

from apps.city.events.events.collapse_in_mines import Event as CollapseInMinesEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_collapse_in_mines_has_choices():
    """Test that the Collapse in Mines event has choices."""
    # Arrange
    savegame = SavegameFactory()
    event = CollapseInMinesEvent(savegame=savegame)

    # Act
    has_choices = event.has_choices()

    # Assert
    assert has_choices is True


@pytest.mark.django_db
def test_collapse_in_mines_returns_two_choices():
    """Test that the Collapse in Mines event returns two choices."""
    # Arrange
    savegame = SavegameFactory()
    event = CollapseInMinesEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert len(choices) == 2


@pytest.mark.django_db
def test_collapse_in_mines_choice_labels():
    """Test the labels of the Collapse in Mines choices."""
    # Arrange
    savegame = SavegameFactory()
    event = CollapseInMinesEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert choices[0].label == "Send rescuers immediately"
    assert choices[1].label == "Seal the tunnels"


@pytest.mark.django_db
def test_collapse_in_mines_choice_effects():
    """Test that choices have effects defined."""
    # Arrange
    savegame = SavegameFactory()
    event = CollapseInMinesEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert len(choices[0].effects) == 2  # Decrease coins and decrease unrest
    assert len(choices[1].effects) == 1  # Just increase unrest


@pytest.mark.django_db
def test_collapse_in_mines_send_rescuers_choice():
    """Test applying the 'send rescuers' choice."""
    # Arrange
    savegame = SavegameFactory(coins=1000, unrest=50)
    initial_coins = savegame.coins
    initial_unrest = savegame.unrest
    event = CollapseInMinesEvent(savegame=savegame)
    choices = event.get_choices()

    # Act
    choices[0].apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins < initial_coins  # Should lose coins
    assert savegame.unrest < initial_unrest  # Should decrease unrest


@pytest.mark.django_db
def test_collapse_in_mines_seal_tunnels_choice():
    """Test applying the 'seal tunnels' choice."""
    # Arrange
    savegame = SavegameFactory(coins=1000, unrest=50)
    initial_coins = savegame.coins
    initial_unrest = savegame.unrest
    event = CollapseInMinesEvent(savegame=savegame)
    choices = event.get_choices()

    # Act
    choices[1].apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins == initial_coins  # Should not lose coins
    assert savegame.unrest > initial_unrest  # Should increase unrest


@pytest.mark.django_db
def test_collapse_in_mines_verbose_text():
    """Test the event description text."""
    # Arrange
    savegame = SavegameFactory()
    event = CollapseInMinesEvent(savegame=savegame)

    # Act
    text = event.get_verbose_text()

    # Assert
    assert "mine" in text.lower()
    assert "collapse" in text.lower()
    assert "workers" in text.lower()


@pytest.mark.django_db
def test_collapse_in_mines_probability():
    """Test that the event has the correct probability."""
    # Arrange
    savegame = SavegameFactory()
    event = CollapseInMinesEvent(savegame=savegame)

    # Act
    probability = event.get_probability()

    # Assert
    assert probability == 3
