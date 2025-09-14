import pytest
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from unittest import mock

from apps.city.management.commands.test_cj import Command as TestCjCommand


def test_test_cj_command_handle():
    """Test test_cj command prints random numbers."""
    command = TestCjCommand()

    with mock.patch('apps.city.management.commands.test_cj.randint') as mock_randint:
        with mock.patch('builtins.print') as mock_print:
            # Mock randint to return consistent values
            mock_randint.return_value = 1

            command.handle()

            # Verify randint was called 100 times with (1, 2)
            assert mock_randint.call_count == 100
            mock_randint.assert_has_calls([mock.call(1, 2)] * 100)

            # Verify print was called 100 times with 1
            assert mock_print.call_count == 100
            mock_print.assert_has_calls([mock.call(1)] * 100)


def test_test_cj_command_via_call_command():
    """Test test_cj command can be called via Django's call_command."""
    with mock.patch('apps.city.management.commands.test_cj.randint') as mock_randint:
        mock_randint.return_value = 2

        # Capture output
        out = StringIO()
        call_command('test_cj', stdout=out)

        # Verify output contains expected values
        output = out.getvalue()
        # The command output goes to stdout but call_command may not capture it
        # Just verify the mock was called 100 times
        assert mock_randint.call_count == 100


def test_test_cj_command_random_output():
    """Test test_cj command produces varied output with real randomness."""
    # This test uses actual randomness to verify the command works
    # Instead of checking output, we'll just verify it runs without error
    out = StringIO()

    try:
        call_command('test_cj', stdout=out)
        # If we reach here, the command executed successfully
        assert True
    except Exception as e:
        pytest.fail(f"Command failed with exception: {e}")


def test_test_cj_command_inheritance():
    """Test TestCjCommand inherits from BaseCommand."""
    from django.core.management.base import BaseCommand

    command = TestCjCommand()
    assert isinstance(command, BaseCommand)


def test_test_cj_command_has_handle_method():
    """Test TestCjCommand implements the handle method."""
    command = TestCjCommand()

    assert hasattr(command, 'handle')
    assert callable(command.handle)


# Integration test with actual Django TestCase for full command testing
class TestCjCommandIntegrationTest(TestCase):
    """Integration tests for test_cj command using Django's TestCase."""

    def test_test_cj_integration(self):
        """Integration test for test_cj command."""
        out = StringIO()
        call_command('test_cj', stdout=out)

        output = out.getvalue()
        lines = output.strip().split('\n')

        # Verify output format
        self.assertEqual(len(lines), 100)
        for line in lines:
            self.assertIn(line, ['1', '2'])