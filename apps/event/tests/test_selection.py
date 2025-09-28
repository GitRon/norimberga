import tempfile
from pathlib import Path
from unittest import mock

import pytest

from apps.event.services.selection import EventSelectionService
from apps.event.tests.factories import (
    HighProbabilityEvent,
    LowProbabilityEvent,
    MockEvent,
    ZeroProbabilityEvent,
)


@pytest.mark.django_db
class TestEventSelectionService:
    """Test suite for EventSelectionService."""

    def test_process_returns_list_of_events(self):
        """Test that process() returns a list of BaseEvent instances."""
        service = EventSelectionService()

        with mock.patch.object(service, "_get_possible_events", return_value=[MockEvent()]):
            result = service.process()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], MockEvent)

    def test_get_possible_events_with_no_apps(self):
        """Test _get_possible_events when no local apps are configured."""
        service = EventSelectionService()

        with mock.patch("django.conf.settings.LOCAL_APPS", []):
            result = service._get_possible_events()

        assert result == []

    def test_get_possible_events_with_no_event_directories(self):
        """Test _get_possible_events when apps have no events/events directories."""
        service = EventSelectionService()

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.nonexistent"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=False),
        ):
            result = service._get_possible_events()

        assert result == []

    def test_get_possible_events_with_empty_event_directory(self):
        """Test _get_possible_events when events directory exists but is empty."""
        service = EventSelectionService()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events_dir = temp_path / "apps" / "test" / "events" / "events"
            events_dir.mkdir(parents=True)

            with (
                mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
                mock.patch("django.conf.settings.ROOT_DIR", temp_path),
                mock.patch("apps.event.services.selection.isdir", return_value=True),
            ):
                result = service._get_possible_events()

        assert result == []

    def test_get_possible_events_ignores_dunder_files(self):
        """Test that _get_possible_events ignores __pycache__ and __init__.py files."""
        service = EventSelectionService()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events_dir = temp_path / "apps" / "test" / "events" / "events"
            events_dir.mkdir(parents=True)

            # Create files that should be ignored
            (events_dir / "__init__.py").touch()
            (events_dir / "__pycache__").mkdir()
            (events_dir / "valid_event.txt").touch()  # Non-Python file

            with (
                mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
                mock.patch("django.conf.settings.ROOT_DIR", temp_path),
                mock.patch("apps.event.services.selection.isdir", return_value=True),
            ):
                result = service._get_possible_events()

        assert result == []

    def test_get_possible_events_handles_import_errors(self):
        """Test that _get_possible_events propagates import errors (current behavior)."""
        service = EventSelectionService()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events_dir = temp_path / "apps" / "test" / "events" / "events"
            events_dir.mkdir(parents=True)

            # Create a Python file
            event_file = events_dir / "broken_event.py"
            event_file.write_text("# This is a broken Python file")

            with (
                mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
                mock.patch("django.conf.settings.ROOT_DIR", temp_path),
                mock.patch("apps.event.services.selection.isdir", return_value=True),
                mock.patch("importlib.import_module", side_effect=ImportError("Module not found")),
                pytest.raises(ImportError),
            ):
                # Should raise ImportError since the code doesn't handle it
                service._get_possible_events()

    def test_get_possible_events_handles_missing_event_class(self):
        """Test that _get_possible_events handles modules without Event class."""
        service = EventSelectionService()

        mock_module = mock.MagicMock()
        del mock_module.Event  # Remove Event attribute to trigger AttributeError

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=True),
            mock.patch("pathlib.Path.iterdir", return_value=[Path("/tmp/test_event.py")]),
            mock.patch("importlib.import_module", return_value=mock_module),
        ):
            result = service._get_possible_events()

        assert result == []

    def test_get_possible_events_handles_non_base_event_classes(self):
        """Test that _get_possible_events ignores classes that aren't BaseEvent instances."""
        service = EventSelectionService()

        class NotAnEvent:
            pass

        mock_module = mock.MagicMock()
        mock_module.Event.return_value = NotAnEvent()

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=True),
            mock.patch("pathlib.Path.iterdir", return_value=[Path("/tmp/test_event.py")]),
            mock.patch("importlib.import_module", return_value=mock_module),
        ):
            result = service._get_possible_events()

        assert result == []

    @mock.patch("random.randint")
    def test_get_possible_events_probability_filtering_high_probability(self, mock_random):
        """Test that events with high probability are included."""
        service = EventSelectionService()
        mock_random.return_value = 50  # Random roll of 50

        mock_module = mock.MagicMock()
        mock_module.Event.return_value = HighProbabilityEvent()  # Probability 90

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=True),
            mock.patch("pathlib.Path.iterdir", return_value=[Path("/tmp/test_event.py")]),
            mock.patch("importlib.import_module", return_value=mock_module),
        ):
            result = service._get_possible_events()

        assert len(result) == 1
        assert isinstance(result[0], HighProbabilityEvent)

    @mock.patch("random.randint")
    def test_get_possible_events_probability_filtering_low_probability(self, mock_random):
        """Test that events with low probability are excluded when random roll is high."""
        service = EventSelectionService()
        mock_random.return_value = 50  # Random roll of 50

        mock_module = mock.MagicMock()
        mock_module.Event.return_value = LowProbabilityEvent()  # Probability 10

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=True),
            mock.patch("pathlib.Path.iterdir", return_value=[Path("/tmp/test_event.py")]),
            mock.patch("importlib.import_module", return_value=mock_module),
        ):
            result = service._get_possible_events()

        assert len(result) == 0

    @mock.patch("random.randint")
    def test_get_possible_events_probability_filtering_zero_probability(self, mock_random):
        """Test that events with zero probability are never included."""
        service = EventSelectionService()
        mock_random.return_value = 1  # Even lowest random roll

        mock_module = mock.MagicMock()
        mock_module.Event.return_value = ZeroProbabilityEvent()  # Probability 0

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=True),
            mock.patch("pathlib.Path.iterdir", return_value=[Path("/tmp/test_event.py")]),
            mock.patch("importlib.import_module", return_value=mock_module),
        ):
            result = service._get_possible_events()

        assert len(result) == 0

    @mock.patch("random.randint")
    def test_get_possible_events_multiple_events_mixed_probabilities(self, mock_random):
        """Test probability filtering with multiple events of different probabilities."""
        service = EventSelectionService()
        mock_random.return_value = 50  # Random roll of 50

        high_prob_module = mock.MagicMock()
        high_prob_module.Event.return_value = HighProbabilityEvent()

        low_prob_module = mock.MagicMock()
        low_prob_module.Event.return_value = LowProbabilityEvent()

        def mock_import(module_name):
            if "high" in module_name:
                return high_prob_module
            return low_prob_module

        with (
            mock.patch("django.conf.settings.LOCAL_APPS", ["apps.test"]),
            mock.patch("django.conf.settings.ROOT_DIR", Path("/tmp")),
            mock.patch("apps.event.services.selection.isdir", return_value=True),
            mock.patch(
                "pathlib.Path.iterdir", return_value=[Path("/tmp/high_prob_event.py"), Path("/tmp/low_prob_event.py")]
            ),
            mock.patch("importlib.import_module", side_effect=mock_import),
        ):
            result = service._get_possible_events()

        # Only high probability event should be included
        assert len(result) == 1
        assert isinstance(result[0], HighProbabilityEvent)

    def test_get_possible_events_file_path_construction(self):
        """Test that file paths are correctly constructed for module importing."""
        service = EventSelectionService()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            events_dir = temp_path / "apps" / "testapp" / "events" / "events"
            events_dir.mkdir(parents=True)

            event_file = events_dir / "sample_event.py"
            event_file.write_text("class Event: pass")

            with (
                mock.patch("django.conf.settings.LOCAL_APPS", ["apps.testapp"]),
                mock.patch("django.conf.settings.ROOT_DIR", temp_path),
                mock.patch("apps.event.services.selection.isdir", return_value=True),
                mock.patch("importlib.import_module") as mock_import,
            ):
                service._get_possible_events()

                # Verify the module path is correctly constructed
                expected_module = "apps.testapp.events.events.sample_event"
                mock_import.assert_called_with(expected_module)

    @mock.patch("random.randint")
    def test_process_end_to_end_integration(self, mock_random):
        """Test the complete process method with real-world scenario simulation."""
        service = EventSelectionService()
        mock_random.return_value = 25  # Random roll of 25

        # Create mock events with different probabilities
        mock_events = [
            HighProbabilityEvent(),  # 90% - should be included
            MockEvent(),  # 50% - should be included
            LowProbabilityEvent(),  # 10% - should be excluded
        ]

        with mock.patch.object(service, "_get_possible_events", return_value=mock_events):
            result = service.process()

        # All mock events should be returned since we're mocking _get_possible_events
        assert len(result) == 3
        assert all(hasattr(event, "get_probability") for event in result)
        assert all(hasattr(event, "get_verbose_text") for event in result)
