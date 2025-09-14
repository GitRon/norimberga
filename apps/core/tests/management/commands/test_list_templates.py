import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.core.management.commands.list_templates import Command as ListTemplatesCommand


def test_list_templates_command_handle():
    """Test list_templates command processes templates correctly."""
    command = ListTemplatesCommand()

    with mock.patch("apps.core.management.commands.list_templates.get_app_template_dirs") as mock_get_dirs:
        with mock.patch.object(command, "list_template_files") as mock_list_files:
            with mock.patch("apps.core.management.commands.list_templates.settings") as mock_settings:
                # Setup mocks
                mock_get_dirs.return_value = ["/app/templates"]
                mock_settings.TEMPLATES = [{"DIRS": ["/global/templates"]}]
                mock_list_files.side_effect = [["/app/templates/app.html"], ["/global/templates/base.html"]]

                with mock.patch.object(command.stdout, "write") as mock_write:
                    command.handle()

                    # Verify app template dirs were retrieved
                    mock_get_dirs.assert_called_once_with("templates")

                    # Verify list_template_files was called for both directories
                    assert mock_list_files.call_count == 2
                    mock_list_files.assert_any_call("/app/templates")
                    mock_list_files.assert_any_call("/global/templates")

                    # Verify output was written
                    expected_output = "/app/templates/app.html\n/global/templates/base.html"
                    mock_write.assert_called_once_with(expected_output)


def test_list_templates_command_list_template_files():
    """Test list_template_files method finds HTML and TXT files."""
    command = ListTemplatesCommand()

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test template files
        template_dir = Path(temp_dir)
        (template_dir / "base.html").write_text("<html></html>")
        (template_dir / "email.txt").write_text("Email content")
        (template_dir / "style.css").write_text("/* CSS */")  # Should be ignored
        (template_dir / "script.js").write_text("// JS")  # Should be ignored

        # Create subdirectory with templates
        subdir = template_dir / "components"
        subdir.mkdir()
        (subdir / "button.html").write_text("<button></button>")

        result = command.list_template_files(str(template_dir))

        # Convert paths to use forward slashes for consistent comparison
        result = [path.replace("\\", "/") for path in result]
        expected_files = [
            str(template_dir / "base.html").replace("\\", "/"),
            str(template_dir / "email.txt").replace("\\", "/"),
            str(subdir / "button.html").replace("\\", "/"),
        ]

        assert len(result) == 3
        for expected_file in expected_files:
            assert expected_file in result


def test_list_templates_command_list_template_files_empty_directory():
    """Test list_template_files with empty directory."""
    command = ListTemplatesCommand()

    with tempfile.TemporaryDirectory() as temp_dir:
        result = command.list_template_files(temp_dir)
        assert result == []


def test_list_templates_command_list_template_files_no_templates():
    """Test list_template_files with directory containing no template files."""
    command = ListTemplatesCommand()

    with tempfile.TemporaryDirectory() as temp_dir:
        template_dir = Path(temp_dir)
        (template_dir / "style.css").write_text("/* CSS */")
        (template_dir / "script.js").write_text("// JS")

        result = command.list_template_files(str(template_dir))
        assert result == []


def test_list_templates_command_via_call_command():
    """Test list_templates command can be called via Django's call_command."""
    with mock.patch("apps.core.management.commands.list_templates.get_app_template_dirs") as mock_get_dirs:
        with mock.patch("apps.core.management.commands.list_templates.settings") as mock_settings:
            # Setup mocks
            mock_get_dirs.return_value = []
            mock_settings.TEMPLATES = [{"DIRS": []}]

            # Capture output
            out = StringIO()
            call_command("list_templates", stdout=out)

            # Verify command executed (should produce empty line since there's a \n.join of empty list)
            output = out.getvalue()
            assert output == "\n"  # Empty join produces just newline


def test_list_templates_command_inheritance():
    """Test ListTemplatesCommand inherits from BaseCommand."""
    from django.core.management.base import BaseCommand

    command = ListTemplatesCommand()
    assert isinstance(command, BaseCommand)


def test_list_templates_command_help_text():
    """Test ListTemplatesCommand has help text."""
    command = ListTemplatesCommand()
    assert command.help == "List all template files"


def test_list_templates_command_has_handle_method():
    """Test ListTemplatesCommand implements the handle method."""
    command = ListTemplatesCommand()

    assert hasattr(command, "handle")
    assert callable(command.handle)


def test_list_templates_command_has_list_template_files_method():
    """Test ListTemplatesCommand implements the list_template_files method."""
    command = ListTemplatesCommand()

    assert hasattr(command, "list_template_files")
    assert callable(command.list_template_files)


# Integration test with actual Django TestCase for full command testing
class ListTemplatesCommandIntegrationTest(TestCase):
    """Integration tests for list_templates command using Django's TestCase."""

    def test_list_templates_integration(self):
        """Integration test for list_templates command with temporary templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test template files
            template_dir = Path(temp_dir)
            (template_dir / "test.html").write_text("<html>Test</html>")
            (template_dir / "email.txt").write_text("Test email")

            # Mock settings to use our temp directory
            with (
                override_settings(
                    TEMPLATES=[
                        {
                            "BACKEND": "django.template.backends.django.DjangoTemplates",
                            "DIRS": [str(template_dir)],
                            "APP_DIRS": True,
                            "OPTIONS": {},
                        }
                    ]
                ),
                mock.patch("apps.core.management.commands.list_templates.get_app_template_dirs") as mock_get_dirs,
            ):
                # Mock app template dirs to return empty list for simpler testing
                mock_get_dirs.return_value = []

                # Run the command
                out = StringIO()
                call_command("list_templates", stdout=out)

                # Verify output contains our test files
                output = out.getvalue()
                self.assertIn("test.html", output)
                self.assertIn("email.txt", output)

    def test_list_templates_integration_with_app_templates(self):
        """Integration test for list_templates command with app templates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test app template structure
            app_template_dir = Path(temp_dir) / "app_templates"
            app_template_dir.mkdir()
            (app_template_dir / "app.html").write_text("<html>App Template</html>")

            global_template_dir = Path(temp_dir) / "global_templates"
            global_template_dir.mkdir()
            (global_template_dir / "base.html").write_text("<html>Base Template</html>")

            # Mock both app and global template directories
            with mock.patch("apps.core.management.commands.list_templates.get_app_template_dirs") as mock_get_dirs:
                with override_settings(
                    TEMPLATES=[
                        {
                            "BACKEND": "django.template.backends.django.DjangoTemplates",
                            "DIRS": [str(global_template_dir)],
                            "APP_DIRS": True,
                            "OPTIONS": {},
                        }
                    ]
                ):
                    mock_get_dirs.return_value = [str(app_template_dir)]

                    # Run the command
                    out = StringIO()
                    call_command("list_templates", stdout=out)

                    # Verify output contains templates from both sources
                    output = out.getvalue()
                    self.assertIn("app.html", output)
                    self.assertIn("base.html", output)
