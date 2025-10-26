import random
from dataclasses import dataclass
from pathlib import Path

import svgwrite

# --- Heraldic constants ---
SHIELD_SHAPES = ["heater", "round", "kite"]
DIVISIONS = ["plain", "per pale", "per fess", "quarterly"]

TINCTURES = {
    "gules": "#d20f0f",  # red
    "azure": "#0033cc",  # blue
    "vert": "#228B22",  # green
    "purpure": "#800080",  # purple
    "sable": "#111111",  # black
    "or": "#ffd700",  # gold
    "argent": "#f0f0f0",  # silver/white
}

CHARGES = ["lion rampant", "eagle displayed", "cross pattee", "fleur-de-lis", "chevron", "bend"]

MOTTOS = [
    None,
    "Fortune favors the bold",
    "Honor and Glory",
    "By Steel and Faith",
    "Ever Forward",
]


@dataclass(kw_only=True)
class HeraldicShield:
    shape: str
    division: str
    tinctures: list[str]
    charges: list[str]
    motto: str | None = None


class CoatOfArmsGeneratorService:
    """Service for generating heraldic coat of arms shields as SVG files."""

    def process(self, *, output_path: str | Path = "shield.svg") -> Path:
        """
        Generate a coat of arms and save it as an SVG file.
        """
        shield = self._generate_shield()
        return self._render_shield_svg(shield=shield, output_path=output_path)

    def _generate_shield(self) -> HeraldicShield:
        """Generate a random heraldic shield with proper heraldic rules."""
        shape = random.choice(SHIELD_SHAPES)
        division = random.choice(DIVISIONS)
        tinctures = random.sample(list(TINCTURES.keys()), k=2)

        # Apply heraldic rule: no metal on metal, no color on color
        tinctures = self._apply_heraldic_rules(tinctures=tinctures)

        charges = random.sample(CHARGES, k=random.randint(1, 2))
        motto = random.choice(MOTTOS)

        return HeraldicShield(shape=shape, division=division, tinctures=tinctures, charges=charges, motto=motto)

    def _apply_heraldic_rules(self, *, tinctures: list[str]) -> list[str]:
        """
        Apply the rule of tincture: no metal on metal, no color on color.
        """
        metals = {"argent", "or"}
        colors = set(TINCTURES.keys()) - metals

        if tinctures[0] in metals and tinctures[1] in metals:
            tinctures[1] = random.choice(list(colors))
        elif tinctures[0] in colors and tinctures[1] in colors:
            tinctures[1] = random.choice(list(metals))

        return tinctures

    def _get_shield_path(self, *, shape: str) -> str:
        """
        Return SVG path data for the given shield shape.
        Paths are designed for a 400x500 viewBox with some padding.
        """
        shield_paths = {
            "heater": "M 50 50 L 350 50 L 350 350 L 200 450 L 50 350 Z",
            # Rounded shield with bezier curves
            "round": "M 50 150 Q 50 50 150 50 L 250 50 Q 350 50 350 150 L 350 350 Q 350 450 200 450 Q 50 450 50 350 Z",
            "kite": "M 200 50 L 320 150 L 280 400 L 200 450 L 120 400 L 80 150 Z",
        }
        # Default to heater if unknown shape
        return shield_paths.get(shape, shield_paths["heater"])

    def _render_shield_svg(self, *, shield: HeraldicShield, output_path: str | Path) -> Path:
        """
        Render a heraldic shield to an SVG file.
        """
        output_path = Path(output_path)
        dwg = svgwrite.Drawing(str(output_path), size=("400px", "500px"))

        # Define the shield shape as a clipping path
        shield_path_data = self._get_shield_path(shape=shield.shape)
        clip_path = dwg.defs.add(dwg.clipPath(id="shield-clip"))
        clip_path.add(dwg.path(d=shield_path_data))

        # Create a group that will be clipped to the shield shape
        shield_group = dwg.g(clip_path="url(#shield-clip)")

        # Background color 1 (fill entire canvas, will be clipped)
        shield_group.add(dwg.rect(insert=(0, 0), size=("400px", "500px"), fill=TINCTURES[shield.tinctures[0]]))

        # Division
        if shield.division == "per pale":
            shield_group.add(dwg.rect(insert=(200, 0), size=(200, 500), fill=TINCTURES[shield.tinctures[1]]))
        elif shield.division == "per fess":
            shield_group.add(dwg.rect(insert=(0, 250), size=(400, 250), fill=TINCTURES[shield.tinctures[1]]))
        elif shield.division == "quarterly":
            shield_group.add(dwg.rect(insert=(0, 0), size=(200, 250), fill=TINCTURES[shield.tinctures[1]]))
            shield_group.add(dwg.rect(insert=(200, 250), size=(200, 250), fill=TINCTURES[shield.tinctures[1]]))

        dwg.add(shield_group)

        # Add the shield outline/border (not clipped)
        dwg.add(
            dwg.path(
                d=shield_path_data,
                fill="none",
                stroke="black",
                stroke_width=3,
            )
        )

        # Charges (text placeholders) - rendered on top of shield
        for i, charge in enumerate(shield.charges):
            dwg.add(
                dwg.text(
                    charge,
                    insert=("50%", f"{45 + i * 15}%"),
                    text_anchor="middle",
                    font_size="16px",
                    fill="white",
                    stroke="black",
                    stroke_width=0.5,
                )
            )

        # Motto at bottom (below shield)
        if shield.motto:
            dwg.add(
                dwg.text(
                    shield.motto,
                    insert=("50%", "95%"),
                    text_anchor="middle",
                    font_size="14px",
                    font_style="italic",
                    fill="black",
                )
            )

        dwg.save()
        return output_path
