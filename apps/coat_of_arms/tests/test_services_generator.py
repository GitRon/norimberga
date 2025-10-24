from pathlib import Path
from unittest import mock

from apps.coat_of_arms.services.generator import (
    CHARGES,
    DIVISIONS,
    MOTTOS,
    SHIELD_SHAPES,
    TINCTURES,
    CoatOfArmsGeneratorService,
    HeraldicShield,
)
from apps.coat_of_arms.tests.factories import HeraldicShieldFactory


def test_apply_heraldic_rules_metal_on_metal():
    """Test that two metals are corrected to metal on color."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    tinctures = ["or", "argent"]

    # Act
    result = service._apply_heraldic_rules(tinctures=tinctures)

    # Assert
    metals = {"argent", "or"}
    colors = set(TINCTURES.keys()) - metals
    assert result[0] in metals
    assert result[1] in colors


def test_apply_heraldic_rules_color_on_color():
    """Test that two colors are corrected to color on metal."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    tinctures = ["gules", "azure"]

    # Act
    result = service._apply_heraldic_rules(tinctures=tinctures)

    # Assert
    metals = {"argent", "or"}
    colors = set(TINCTURES.keys()) - metals
    assert result[0] in colors
    assert result[1] in metals


def test_apply_heraldic_rules_metal_on_color():
    """Test that metal on color is left unchanged."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    tinctures = ["or", "gules"]

    # Act
    result = service._apply_heraldic_rules(tinctures=tinctures)

    # Assert
    assert result == ["or", "gules"]


def test_apply_heraldic_rules_color_on_metal():
    """Test that color on metal is left unchanged."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    tinctures = ["azure", "argent"]

    # Act
    result = service._apply_heraldic_rules(tinctures=tinctures)

    # Assert
    assert result == ["azure", "argent"]


def test_generate_shield_returns_valid_shield():
    """Test that _generate_shield returns a HeraldicShield with valid attributes."""
    # Arrange
    service = CoatOfArmsGeneratorService()

    # Act
    shield = service._generate_shield()

    # Assert
    assert isinstance(shield, HeraldicShield)
    assert shield.shape in SHIELD_SHAPES
    assert shield.division in DIVISIONS
    assert len(shield.tinctures) == 2
    assert all(t in TINCTURES for t in shield.tinctures)
    assert 1 <= len(shield.charges) <= 2
    assert all(c in CHARGES for c in shield.charges)
    assert shield.motto is None or shield.motto in MOTTOS


def test_generate_shield_follows_heraldic_rules():
    """Test that _generate_shield produces tinctures following heraldic rules."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    metals = {"argent", "or"}
    colors = set(TINCTURES.keys()) - metals

    # Act - test multiple generations to ensure rules are always followed
    for _ in range(20):
        shield = service._generate_shield()

        # Assert
        tincture1, tincture2 = shield.tinctures
        both_metals = tincture1 in metals and tincture2 in metals
        both_colors = tincture1 in colors and tincture2 in colors
        assert not both_metals, "Shield should not have metal on metal"
        assert not both_colors, "Shield should not have color on color"


def test_render_shield_svg_creates_file(tmp_path):
    """Test that _render_shield_svg creates an SVG file."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create()
    output_path = tmp_path / "test_shield.svg"

    # Act
    result = service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    assert result == output_path
    assert output_path.exists()
    assert output_path.is_file()


def test_render_shield_svg_creates_valid_svg_content(tmp_path):
    """Test that _render_shield_svg creates a valid SVG with expected content."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create(
        division="per pale",  # This division will use both tinctures
        tinctures=["gules", "argent"],
        charges=["lion rampant", "eagle displayed"],
        motto="Fortune favors the bold",
    )
    output_path = tmp_path / "test_shield.svg"

    # Act
    service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    content = output_path.read_text()
    assert "<?xml" in content or "<svg" in content
    assert "lion rampant" in content
    assert "eagle displayed" in content
    assert "Fortune favors the bold" in content
    assert TINCTURES["gules"] in content
    assert TINCTURES["argent"] in content


def test_render_shield_svg_handles_plain_division(tmp_path):
    """Test that plain division creates only one background color."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create(division="plain", tinctures=["gules", "argent"])
    output_path = tmp_path / "test_shield.svg"

    # Act
    service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    content = output_path.read_text()
    assert TINCTURES["gules"] in content
    # For plain division, second tincture may not appear in the SVG


def test_render_shield_svg_handles_per_pale_division(tmp_path):
    """Test that per pale division creates two vertical sections."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create(division="per pale", tinctures=["gules", "argent"])
    output_path = tmp_path / "test_shield.svg"

    # Act
    service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    content = output_path.read_text()
    assert TINCTURES["gules"] in content
    assert TINCTURES["argent"] in content


def test_render_shield_svg_handles_per_fess_division(tmp_path):
    """Test that per fess division creates two horizontal sections."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create(division="per fess", tinctures=["azure", "or"])
    output_path = tmp_path / "test_shield.svg"

    # Act
    service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    content = output_path.read_text()
    assert TINCTURES["azure"] in content
    assert TINCTURES["or"] in content


def test_render_shield_svg_handles_quarterly_division(tmp_path):
    """Test that quarterly division creates four sections."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create(division="quarterly", tinctures=["vert", "argent"])
    output_path = tmp_path / "test_shield.svg"

    # Act
    service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    content = output_path.read_text()
    assert TINCTURES["vert"] in content
    assert TINCTURES["argent"] in content


def test_render_shield_svg_without_motto(tmp_path):
    """Test that shield renders correctly without a motto."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create(motto=None)
    output_path = tmp_path / "test_shield.svg"

    # Act
    result = service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    assert result == output_path
    assert output_path.exists()


def test_render_shield_svg_accepts_string_path(tmp_path):
    """Test that _render_shield_svg accepts a string path."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    shield = HeraldicShieldFactory.create()
    output_path = str(tmp_path / "test_shield.svg")

    # Act
    result = service._render_shield_svg(shield=shield, output_path=output_path)

    # Assert
    assert isinstance(result, Path)
    assert result.exists()


def test_process_generates_and_saves_shield(tmp_path):
    """Test that process method generates a shield and saves it to the specified path."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    output_path = tmp_path / "generated_shield.svg"

    # Act
    result = service.process(output_path=output_path)

    # Assert
    assert result == output_path
    assert output_path.exists()
    assert output_path.is_file()


def test_process_creates_valid_svg(tmp_path):
    """Test that process method creates a valid SVG file."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    output_path = tmp_path / "generated_shield.svg"

    # Act
    service.process(output_path=output_path)

    # Assert
    content = output_path.read_text()
    assert "<?xml" in content or "<svg" in content


def test_process_uses_default_filename(tmp_path, monkeypatch):
    """Test that process method uses default filename when not specified."""
    # Arrange
    monkeypatch.chdir(tmp_path)
    service = CoatOfArmsGeneratorService()

    # Act
    result = service.process()

    # Assert
    assert result == Path("shield.svg")
    assert Path("shield.svg").exists()


def test_process_calls_generate_and_render(tmp_path):
    """Test that process method calls both _generate_shield and _render_shield_svg."""
    # Arrange
    service = CoatOfArmsGeneratorService()
    output_path = tmp_path / "test_shield.svg"

    with (
        mock.patch.object(service, "_generate_shield", wraps=service._generate_shield) as mock_generate,
        mock.patch.object(service, "_render_shield_svg", wraps=service._render_shield_svg) as mock_render,
    ):
        # Act
        service.process(output_path=output_path)

        # Assert
        mock_generate.assert_called_once()
        mock_render.assert_called_once()
