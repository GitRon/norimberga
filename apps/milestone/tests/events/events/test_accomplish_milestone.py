from unittest.mock import patch

import pytest
from django.contrib import messages

from apps.city.tests.factories import SavegameFactory
from apps.milestone.events.events.accomplish_milestone import Event
from apps.milestone.models import MilestoneLog


@pytest.mark.django_db
class TestAccomplishMilestoneEvent:
    def test_event_constants(self):
        # Arrange & Act
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Assert
        assert event.LEVEL == messages.SUCCESS
        assert event.TITLE == "Milestone accomplished"

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_event_initialization_creates_savegame(self, mock_is_accomplished):
        # Arrange & Act
        mock_is_accomplished.return_value = False
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Assert
        assert event.savegame is not None
        assert event.savegame.id == savegame.id
        assert event.accomplish_milestones == []

    def test_event_initialization_with_existing_savegame(self):
        # Arrange
        existing_savegame = SavegameFactory()

        # Act
        event = Event(savegame=existing_savegame)

        # Assert
        assert event.savegame.id == existing_savegame.id

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_event_probability_zero_when_no_milestones_accomplished(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = False

        # Act
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Assert
        assert event.get_probability() == 0
        assert len(event.accomplish_milestones) == 0

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_event_probability_hundred_when_milestone_accomplished(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = True

        # Act
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Assert
        assert event.get_probability() == 100
        assert len(event.accomplish_milestones) == 1

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_prepare_effect_accomplish_milestone_returns_none_when_no_milestones(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = False
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Act
        result = event._prepare_effect_accomplish_milestone()

        # Assert
        assert result is None

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_prepare_effect_accomplish_milestone_returns_effect_when_milestone_exists(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = True
        savegame = SavegameFactory(current_year=1200)
        event = Event(savegame=savegame)

        # Act
        result = event._prepare_effect_accomplish_milestone()

        # Assert
        assert result is not None
        assert result.savegame_id == savegame.id
        assert result.current_year == 1200
        assert "GrowCityMilestone" in result.milestone

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_get_verbose_text_with_no_milestones(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = False
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Act
        result = event.get_verbose_text()

        # Assert
        expected = 'Your prosperous city has accomplished a new milestone! Rejoice that "" has been achieved.'
        assert result == expected

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_get_verbose_text_with_milestone(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = True
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Act
        result = event.get_verbose_text()

        # Assert
        assert "Your prosperous city has accomplished a new milestone!" in result
        assert "GrowCityMilestone" in result
        assert "has been achieved." in result

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_get_effects_returns_empty_list_when_no_milestones(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = False
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Act
        effects = event.get_effects()

        # Assert
        assert effects == [None]  # _prepare_effect_accomplish_milestone returns None

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_get_effects_returns_accomplish_milestone_effect_when_milestone_exists(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = True
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Act
        effects = event.get_effects()

        # Assert
        assert len(effects) == 1
        assert effects[0] is not None
        assert hasattr(effects[0], "process")

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_process_creates_milestone_log_when_milestone_accomplished(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = True
        savegame = SavegameFactory(current_year=1200)
        event = Event(savegame=savegame)

        # Act
        result = event.process()

        # Assert
        assert MilestoneLog.objects.count() == 1
        milestone_log = MilestoneLog.objects.first()
        assert milestone_log.savegame_id == savegame.id
        assert milestone_log.accomplished_at == 1200
        assert "GrowCityMilestone" in milestone_log.milestone
        assert "Your prosperous city has accomplished a new milestone!" in result

    @patch("apps.milestone.milestones.grow_city.GrowCityMilestone.is_accomplished")
    def test_process_does_not_create_milestone_log_when_no_milestone_accomplished(self, mock_is_accomplished):
        # Arrange
        mock_is_accomplished.return_value = False
        savegame = SavegameFactory()
        event = Event(savegame=savegame)

        # Act
        result = event.process()

        # Assert
        assert MilestoneLog.objects.count() == 0
        assert result is not None  # Still returns verbose text
