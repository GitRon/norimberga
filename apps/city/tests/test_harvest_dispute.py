import pytest

from apps.city.events.events.harvest_dispute import Event as HarvestDisputeEvent
from apps.savegame.tests.factories import SavegameFactory


@pytest.mark.django_db
def test_harvest_dispute_has_choices():
    """Test that the Harvest Dispute event has choices."""
    # Arrange
    savegame = SavegameFactory()
    event = HarvestDisputeEvent(savegame=savegame)

    # Act
    has_choices = event.has_choices()

    # Assert
    assert has_choices is True


@pytest.mark.django_db
def test_harvest_dispute_returns_two_choices():
    """Test that the Harvest Dispute event returns two choices."""
    # Arrange
    savegame = SavegameFactory()
    event = HarvestDisputeEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert len(choices) == 2


@pytest.mark.django_db
def test_harvest_dispute_choice_labels():
    """Test the labels of the Harvest Dispute choices."""
    # Arrange
    savegame = SavegameFactory()
    event = HarvestDisputeEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert choices[0].label == "Conduct a thorough investigation"
    assert choices[1].label == "Make an arbitrary ruling"


@pytest.mark.django_db
def test_harvest_dispute_choice_effects():
    """Test that choices have effects defined."""
    # Arrange
    savegame = SavegameFactory()
    event = HarvestDisputeEvent(savegame=savegame)

    # Act
    choices = event.get_choices()

    # Assert
    assert len(choices[0].effects) == 2  # Decrease coins and decrease unrest
    assert len(choices[1].effects) == 1  # Just increase unrest


@pytest.mark.django_db
def test_harvest_dispute_investigate_choice():
    """Test applying the 'investigate' choice."""
    # Arrange
    savegame = SavegameFactory(coins=1000, unrest=50)
    initial_coins = savegame.coins
    initial_unrest = savegame.unrest
    event = HarvestDisputeEvent(savegame=savegame)
    choices = event.get_choices()

    # Act
    choices[0].apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins < initial_coins  # Should lose coins for investigation
    assert savegame.unrest < initial_unrest  # Should decrease unrest


@pytest.mark.django_db
def test_harvest_dispute_arbitrary_ruling_choice():
    """Test applying the 'arbitrary ruling' choice."""
    # Arrange
    savegame = SavegameFactory(coins=1000, unrest=50)
    initial_coins = savegame.coins
    initial_unrest = savegame.unrest
    event = HarvestDisputeEvent(savegame=savegame)
    choices = event.get_choices()

    # Act
    choices[1].apply_effects(savegame=savegame)

    # Assert
    savegame.refresh_from_db()
    assert savegame.coins == initial_coins  # Should not lose coins
    assert savegame.unrest > initial_unrest  # Should increase unrest


@pytest.mark.django_db
def test_harvest_dispute_verbose_text():
    """Test the event description text."""
    # Arrange
    savegame = SavegameFactory()
    event = HarvestDisputeEvent(savegame=savegame)

    # Act
    text = event.get_verbose_text()

    # Assert
    assert "farmer" in text.lower()
    assert "grain" in text.lower()
    assert "dispute" in text.lower() or "accuse" in text.lower()


@pytest.mark.django_db
def test_harvest_dispute_probability():
    """Test that the event has the correct probability."""
    # Arrange
    savegame = SavegameFactory()
    event = HarvestDisputeEvent(savegame=savegame)

    # Act
    probability = event.get_probability()

    # Assert
    assert probability == 3
